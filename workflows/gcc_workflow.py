from typing import Union, get_args, get_origin, get_type_hints
from gha.core import GhaDecorator
from gha.workflow import _Workflow


class WorkflowDecorator(GhaDecorator[_Workflow]):
    pass


def main():
    # workflow = Workflow(
    #     name="Publish",
    #     on=Events(
    #         push=PushEventTrigger(
    #             tags=["v*"],
    #         )
    #     ),
    #     permissions=Permissions(
    #         id_token="write",
    #         contents="write",
    #         packages="write",
    #         pull_requests="write",
    #     ),
    #     jobs={
    #         "test": Job(
    #             name="Test job",
    #             runs_on="ubuntu-latest",
    #             outputs={
    #                 "upload_url": "${{ steps.create_release.outputs.upload_url }}",
    #             },
    #             steps=[
    #                 CheckoutActionV4(
    #                     name="Checkout",
    #                     with_options=CheckoutActionV4Options(fetch_depth=0),
    #                 ),
    #                 ShellAction(
    #                     name="Create release",
    #                     id="create_release",
    #                     run='echo "upload_url=hello" >> "$GITHUB_OUTPUT"',
    #                 ),
    #             ],
    #         )
    #     },
    # )

    def is_optional_type(annotation):
        origin = get_origin(annotation)
        args = get_args(annotation)
        return origin is Union and type(None) in args

    # with open("workflow.yaml", "w", encoding="utf8") as out:
    #     out.write(workflow.to_yaml())
    print(WorkflowDecorator("jobs").complex)


if __name__ == "__main__":
    main()
