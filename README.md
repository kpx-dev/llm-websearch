# LLM Websearch Workshop

## Getting Started


## Workshop Admin 

Launch the stack: 

```bash
aws cloudformation create-stack \
--region us-west-2 \
--stack-name llm-websearch-workshop \
--template-body file://cfn/workshop.yaml \
--capabilities CAPABILITY_IAM
```