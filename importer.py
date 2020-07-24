from github import Github
from jinja2 import Environment, FileSystemLoader
import os
import logging
import json

GITHUB_ORG = "gifkoek-org"
# GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_TOKEN = ""

# set logger details
FORMAT = "%(levelname)s %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_constellation_name(team):
    if team in ["foobar"]:
        return "scorpio"
    else:
        return "orphanedConstellation"


def get_all_repos(gclient):
    repo_list = []
    for repo in gclient.get_user().get_repos():
        this_repo = {}
        logger.info(f"{repo.name}, "
                    f"{repo.description}"
                    f"{repo.default_branch}, "
                    f"{repo.archived}, "
                    f"XXXTOPICS{repo.get_topics()}, "
                    f"XXXTEAMS{repo.get_teams()}"
                    # f"{repo.permissions}, "
                    # f"{repo.owner}, "
                    )

        # get teams and their push/pull (write/read) permissions on this repo
        writer_teams = []
        # writer_teams = []
        for team in repo.get_teams():
            logger.info(f"teams are {team} with permission {team.permission}")
            if team.permission == "push" or team.permission == "admin":
                writer_teams.append(team.id)

        # get master branch protections, if they exist
        owner_teams = []
        constellation = ""
        if repo.default_branch == "master":
            branch = repo.get_branch("master")
            if branch.protected:
                logger.info(f"branch has protection")
                try:
                    for team in branch.get_team_push_restrictions():
                        owner_teams.append(team.id)
                        constellation = get_constellation_name(team.name)
                except Exception as e:
                    logger.info(f"branch {branch} has no push restrictions.\n Exception is: {e}")
                    owner_teams.append("orphanedRepo")
            else:
                logger.info(f"branch has no protection")
                owner_teams.append("orphanedRepo")
        else:
            logger.info(f"XXX {repo.name} has a default branch other than 'master'!")
            owner_teams.append("orphanedRepo")

        this_repo["name"] = repo.name
        this_repo["description"] = repo.description
        this_repo["auto_init"] = False
        this_repo["archived"] = repo.archived
        this_repo["writer_teams"] = writer_teams
        this_repo["owner_teams"] = owner_teams
        this_repo["constellation"] = constellation

        logger.info(f"object for this repo: {json.dumps(this_repo, indent=4)}")
        #append to the global list
        repo_list.append(this_repo)

    logger.info(f"repo dict:\n {json.dumps(repo_list, indent=4)}")
    return repo_list


def build_templates(repo_list):
    file_loader = FileSystemLoader(".")
    env = Environment(loader=file_loader)
    env.trim_blocks = True
    env.lstrip_blocks = True
    env.rstrip_blocks = True

    # build the tf file
    template = env.get_template("terraform.j2")
    output = template.render(repo_list=repo_list)
    logger.info(output)

    # build the resource import file
    template = env.get_template("resource.j2")
    output = template.render(repo_list=repo_list)
    logger.info(output)


def main():
    gclient = Github(GITHUB_TOKEN)
    # repo_list = get_all_repos(gclient)
    repo_list = [
        {
            "name": "terraform-provider-aws",
            "description": "Terraform AWS provider",
            "auto_init": False,
            "archived": False,
            "writer_teams": [],
            "owner_teams": [
                "orphanedRepo"
            ],
            "constellation": ""
        },
        {
            "name": "aacorne-testing2",
            "description": "Testing repo creation with TF",
            "auto_init": False,
            "archived": False,
            "writer_teams": [
                3459189,
                3937005
            ],
            "owner_teams": [
                3937005
            ],
            "constellation": "orphanedConstellation"
        },
        {
            "name": "aws-lambda-deployments",
            "description": "testing aws lambda codepipelines",
            "auto_init": False,
            "archived": False,
            "writer_teams": [
                3459189
            ],
            "owner_teams": [
                "orphanedRepo"
            ],
            "constellation": ""
        }
    ]

    build_templates(repo_list)



main()

# all_repos =  [
#     {
#         "name": "terraform-provider-aws",
#         "description": "Terraform AWS provider",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [],
#         "owner_teams": [
#             "orphanedRepo"
#         ],
#         "constellation": ""
#     },
#     {
#         "name": "aacorne-testing2",
#         "description": "Testing repo creation with TF",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189,
#             3937005
#         ],
#         "owner_teams": [
#             3937005
#         ],
#         "constellation": "orphanedConstellation"
#     },
#     {
#         "name": "aws-lambda-deployments",
#         "description": "testing aws lambda codepipelines",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189
#         ],
#         "owner_teams": [
#             "orphanedRepo"
#         ],
#         "constellation": ""
#     },
#     {
#         "name": "aws-lambda-deployments-safemode",
#         "description": "Lambda deployments in safe mode",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189
#         ],
#         "owner_teams": [
#             "orphanedRepo"
#         ],
#         "constellation": ""
#     },
#     {
#         "name": "aws-testing",
#         "description": "aws-testing",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189,
#             3937005
#         ],
#         "owner_teams": [
#             3937005
#         ],
#         "constellation": "orphanedConstellation"
#     },
#     {
#         "name": "cfn-nested-stacks-pipeline",
#         "description": "Pipeline to automate deployment of nested CFN stacks",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189
#         ],
#         "owner_teams": [
#             "orphanedRepo"
#         ],
#         "constellation": ""
#     },
#     {
#         "name": "cfn-nested-stacks-simpleexample",
#         "description": "Simple example to test nested CFN stacks",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189
#         ],
#         "owner_teams": [
#             "orphanedRepo"
#         ],
#         "constellation": ""
#     },
#     {
#         "name": "codepipeline-cfntemplate",
#         "description": "CloudFormation template to build a CodePipeline",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189
#         ],
#         "owner_teams": [
#             "orphanedRepo"
#         ],
#         "constellation": ""
#     },
#     {
#         "name": "codepipeline-simpleexample",
#         "description": "Simple test for basic CFN template with CodePipeline",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189
#         ],
#         "owner_teams": [
#             "orphanedRepo"
#         ],
#         "constellation": ""
#     },
#     {
#         "name": "ecs-refarch-cloudformation",
#         "description": "A reference architecture for deploying containerized microservices with Amazon ECS and AWS CloudFormation (YAML)",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189
#         ],
#         "owner_teams": [
#             "orphanedRepo"
#         ],
#         "constellation": ""
#     },
#     {
#         "name": "esp8266",
#         "description": "personal esp8266 projects",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189
#         ],
#         "owner_teams": [
#             "orphanedRepo"
#         ],
#         "constellation": ""
#     },
#     {
#         "name": "github-iac",
#         "description": "Terraform IaC for Github",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189
#         ],
#         "owner_teams": [
#             "orphanedRepo"
#         ],
#         "constellation": ""
#     },
#     {
#         "name": "github-terrafom-importer",
#         "description": "python script to get current github configuration and create terraform code for it",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189
#         ],
#         "owner_teams": [
#             3459189
#         ],
#         "constellation": "scorpio"
#     },
#     {
#         "name": "lambda-versioning-the-hard-way",
#         "description": "Pipelines and CloudFormation template for safe-mode Lambda deploys without using SAM",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189,
#             3937005
#         ],
#         "owner_teams": [
#             3937005
#         ],
#         "constellation": "orphanedConstellation"
#     },
#     {
#         "name": "pipeline-variable-replacer",
#         "description": "CodePipeline for a Lambda function to do Jinja-based variable replacement in CloudFormation YAML files",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189
#         ],
#         "owner_teams": [
#             "orphanedRepo"
#         ],
#         "constellation": ""
#     },
#     {
#         "name": "private-APIgw-with-custom-dns",
#         "description": null,
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189
#         ],
#         "owner_teams": [
#             "orphanedRepo"
#         ],
#         "constellation": ""
#     },
#     {
#         "name": "terraform-modules",
#         "description": null,
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [],
#         "owner_teams": [
#             "orphanedRepo"
#         ],
#         "constellation": ""
#     },
#     {
#         "name": "variable-replacer",
#         "description": "Lambda function to do Jinja-based variable replacement in CloudFormation YAML files",
#         "auto_init": false,
#         "archived": false,
#         "writer_teams": [
#             3459189
#         ],
#         "owner_teams": [
#             "orphanedRepo"
#         ],
#         "constellation": ""
#     }
# ]

