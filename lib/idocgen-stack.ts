import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
// import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as lambda from "aws-cdk-lib/aws-lambda";

export class IdocgenStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

    // example resource
    // const queue = new sqs.Queue(this, 'IdocgenQueue', {
    //   visibilityTimeout: cdk.Duration.seconds(300)
    // });

    const swarm_agents_function = new lambda.DockerImageFunction(
      this,
      "SwarmAgentsFunction",
      {
        code: lambda.DockerImageCode.fromImageAsset("./images/swarm_agents"),
        memorySize: 1024,
        timeout: cdk.Duration.seconds(15),
        description: "idocgen:swarm_agents",
      }
    );

    const swarm_agents_url = swarm_agents_function.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ["*"],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ["*"],
      },
    });

    new cdk.CfnOutput(this, "SwarmAgentsUrl", {
      value: swarm_agents_url.url,
    });

    const csv_maker_function = new lambda.DockerImageFunction(
      this,
      "CsvMakerFunction",
      {
        code: lambda.DockerImageCode.fromImageAsset("./images/csv_maker"),
        memorySize: 1024,
        timeout: cdk.Duration.seconds(15),
        description: "idocgen:csv_maker",
      }
    );

    const csv_maker_url = csv_maker_function.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ["*"],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ["*"],
      },
    });

    new cdk.CfnOutput(this, "CsvMakerUrl", {
      value: csv_maker_url.url,
    });
  }
}
