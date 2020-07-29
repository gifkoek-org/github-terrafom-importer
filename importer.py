from github import Github
from jinja2 import Environment, FileSystemLoader
import os
import logging
import json

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

# set logger details
FORMAT = "%(levelname)s %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_constellation_name(team):
    if team.lower() in ["teamnameyourelookingfor"]:
        return "matchingconstellationname"
    else:
        return "orphanedConstellation"


def get_writer_teams(repo):
    logger.info(f"getting writer teams for repo '{repo.name}'")
    writer_teams = []

    try:
        for team in repo.get_teams():
            logger.info(f"on repo '{repo.name}' team '{team}' has permission '{team.permission}'")
            if team.permission == "push" or team.permission == "admin":
                writer_teams.append(team.name)
        return writer_teams
    except Exception as e:
        logger.warning(f"issue with teams for repo {repo.name}, Exception is {e}")
        writer_teams.append("noWriterTeamDefined")
        return writer_teams


def get_owner_teams(repo):
    logger.info(f"getting owner teams for repo '{repo.name}'")
    owner_teams = []

    # i'm sure these try/except, if/else's below can be done in a better way...
    try:
        if repo.default_branch:             # is there a default branch?
            branch = repo.get_branch(repo.default_branch)
            if branch.protected:            # is the branch protected?
                logger.info(f"branch '{branch.name}' is protected")
                try:
                    for team in branch.get_team_push_restrictions():
                        owner_teams.append(team.name)
                        constellation = get_constellation_name(team.name)
                        return owner_teams, constellation
                    else:
                        owner_teams.append("orphanedRepo")
                        constellation = "orphanedConstellation"
                        return owner_teams, constellation
                except Exception as e:
                    logger.warning(f"branch {branch} has no push restrictions.\n Exception is: {e}")
                    owner_teams.append("orphanedRepo")
                    constellation = "orphanedConstellation"
                    return owner_teams, constellation
            else:
                logger.info(f"branch has no protection")
                owner_teams.append("orphanedRepo")
                constellation = "orphanedConstellation"
                return owner_teams, constellation
    except:
        logger.error(f"XXX '{repo.name}' has NO default branch PANIC!")
        owner_teams.append("orphanedRepo")
        constellation = "orphanedConstellation"
        return owner_teams, constellation


def get_all_repos(gclient):
    repo_list = []
    for repo in gclient.get_user().get_repos():
        this_repo = {}
        logger.info(f"{repo.name}, "
                    f"{repo.description}, "
                    f"{repo.default_branch}, "
                    f"{repo.archived}, "
                    f"{repo.owner}, "
                    )

        # get teams and their push/pull (write/read) permissions on this repo
        writer_teams = get_writer_teams(repo)

        # get master branch protections, if they exist
        owner_teams, constellation = get_owner_teams(repo)

        # build the repo json object
        this_repo["name"] = repo.name
        this_repo["description"] = repo.description
        this_repo["auto_init"] = False
        this_repo["archived"] = repo.archived
        this_repo["writer_teams"] = writer_teams
        this_repo["owner_teams"] = owner_teams
        this_repo["constellation"] = constellation

        logger.info(f"object for this repo: {json.dumps(this_repo, indent=4)}")
        repo_list.append(this_repo)     #append to the global list

    return repo_list


def split_repos_by_team(repo_list, prefix):
    # return only those repos that start with the prefix
    prefixed_repos = []
    logger.info(f"finding all repos starting with '{prefix}'")
    for repo in repo_list:
        if repo["name"].startswith(prefix):
            prefixed_repos.append(repo)
            logger.info(f"added repo \'{repo['name']}\' to the prefixed list")

    logger.info(f"filtered {len(prefixed_repos)} repos from total of {len(repo_list)}")

    return prefixed_repos


def build_templates(repo_list, prefix):
    file_loader = FileSystemLoader(".")     # template files are in this directory
    env = Environment(loader=file_loader)
    env.trim_blocks = True                  # strip white space
    env.lstrip_blocks = True
    env.rstrip_blocks = True

    # build the tf file
    template = env.get_template("terraform.j2")
    terraform_output = template.render(repo_list=repo_list)
    logger.info(terraform_output)

    # build the resource import file
    template = env.get_template("resource.j2")
    resource_import = template.render(repo_list=repo_list)
    logger.info(resource_import)

    # write to a file
    with open(f"{prefix}repos.tf", "w") as tffile:
        tffile.write(terraform_output)
    with open(f"{prefix}resource.yaml", "w") as resourcefile:
        resourcefile.write(resource_import)


def main():
    gclient = Github(GITHUB_TOKEN)
    # repo_list = get_all_repos(gclient)
    # logger.info(json.dumps(repo_list, indent=4))

    # so we don't have to re-get all the repos, because it takes long
    # with open("repolist_file", "w") as repofile:
    #     json.dump(repo_list, repofile)

    with open("repolist_file", "r") as repofile:
        repo_list = json.load(repofile)

    # logger.info(json.dumps(repo_list, indent=4))
    # render the templates per listed repo prefix
    repo_prefix_list = ["changetorequiredstring"]
    for prefix in repo_prefix_list:
        build_templates(split_repos_by_team(repo_list, prefix), prefix)

main()
