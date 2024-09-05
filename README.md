# LLM Websearch Workshop

## Getting Started
To get started with the notebook examples, ensure you have access to [Amazon Bedrock](https://aws.amazon.com/bedrock/). 
- Ensure you have gone to the Bedrock models access page in the AWS Console and enabled acceess to `Anthropic Claude 3.5 Sonnet` and `Claude 3 Haiku` models.

Then clone this repo and launch the CloudFormation stack to create a SageMaker notebook which has the permissions and role already defined for you:

```bash
aws cloudformation create-stack \
--region us-west-2 \
--stack-name llm-websearch-workshop \
--template-body file://cfn/workshop.yaml \
--capabilities CAPABILITY_IAM
```
## Open the SageMaker notebook
- In the AWS console, navigate to the CloudFormation page and select the `llm-websearch-workshop` stack
- In the Outputs tab, click on the URL link named `NoteBookLocation` to open the JupyterLab notebook

## Install the required Python modules
- From within the JupyterLab notebook, open a new terminal
- At the terminal console, run the following command:
```bash
pip install -r requirements.txt
```

## Launch the sample notebook
- In the JupyterLab File Browser, doubleclick on the notebook `.ipynb` file
- If you are prompted to select a kernal type, choose `conda_python3`
- Follow the instructions provided in the notebook to complete the workshop

## Running the notebook in your own environment without using CloudFormation
### Enable AWS IAM permissions for Bedrock

The AWS identity you assume from your environment (which is the [*Studio/notebook Execution Role*](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html) from SageMaker, or could be a role or IAM User for self-managed notebooks or other use-cases), must have sufficient [AWS IAM permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html) to call the Amazon Bedrock service.

To grant Bedrock access to your identity, you can:

- Open the [AWS IAM Console](https://us-east-1.console.aws.amazon.com/iam/home?#)
- Find your [Role](https://us-east-1.console.aws.amazon.com/iamv2/home?#/roles) (if using SageMaker or otherwise assuming an IAM Role), or else [User](https://us-east-1.console.aws.amazon.com/iamv2/home?#/users)
- Select *Add Permissions > Create Inline Policy* to attach new inline permissions, open the *JSON* editor and paste in the below example policy:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockFullAccess",
            "Effect": "Allow",
            "Action": ["bedrock:*"],
            "Resource": "*"
        }
    ]
}
```

> ⚠️ **Note:** With Amazon SageMaker, your notebook execution role will typically be *separate* from the user or role that you log in to the AWS Console with. If you'd like to explore the AWS Console for Amazon Bedrock, you'll need to grant permissions to your Console user/role too.

For more information on the fine-grained action and resource permissions in Bedrock, check out the Bedrock Developer Guide.

## Contributing

We welcome community contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file.
