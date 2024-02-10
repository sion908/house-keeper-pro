import * as cdk from "aws-cdk-lib";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as iam from "aws-cdk-lib/aws-iam";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as signer from "aws-cdk-lib/aws-signer";
import { aws_logs as logs } from 'aws-cdk-lib';
import { Construct } from "constructs";
import * as fs from "fs";
import * as path from "path";
import * as yaml from "yaml";
import { getConfig, ENVS } from "./env";

interface StampRallyStackProps extends cdk.StackProps {
  stageName:string;
}

export class StampRallyStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: StampRallyStackProps) {
    super(scope, id, props);
    // deploy時の引数 or envファイル参照で行う

    const stageName = props?.stageName || ENVS.DEV;

    const signingProfile = new signer.SigningProfile(this, "SigningProfile", {
      platform: signer.Platform.AWS_LAMBDA_SHA384_ECDSA,
    });


    const codeSigningConfig = new lambda.CodeSigningConfig(
      this,
      "CodeSigningConfig",
      {
        signingProfiles: [signingProfile],
      }
    );

    const environment = getConfig(stageName);

    // レイヤー作成
    const layer = new lambda.LayerVersion(this, `SRLayer-${stageName}`, {
      code: lambda.Code.fromAsset("./api/python_modules/dependencies.zip"),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_10],
      description: "A layer to hold the FastAPI and Mangum dependencies",
    });

    // Lambda関数の作成
    const fn = new lambda.Function(this, `SRhandler-${stageName}`, {
      codeSigningConfig,
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: "main.handler",
      code: lambda.Code.fromAsset(path.join(__dirname, "../api/src"),{
        exclude: ['alembic.ini', 'tests', 'database/migrations','__pycache__']
      }),
      layers: [layer], // レイヤーを設定
      environment: {
        ...environment
      },
      timeout: cdk.Duration.seconds( 3 * 60 ),
      memorySize: 256,
      logRetention: stageName==ENVS.PROD? logs.RetentionDays.SIX_MONTHS : logs.RetentionDays.ONE_WEEK
    });

    const lineFn = new lambda.Function(this, `SRLinehandler-${stageName}`, {
      codeSigningConfig,
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: "line_event.line_handler",
      code: lambda.Code.fromAsset(path.join(__dirname, "../api/src"),{
        exclude: ['alembic.ini', 'tests', 'database/migrations','__pycache__']
      }),
      layers: [layer], // レイヤーを設定
      environment: {
        ...environment
      },
      timeout: cdk.Duration.seconds( 3 * 60 ),
      memorySize: 256,
      logRetention: stageName==ENVS.PROD? logs.RetentionDays.SIX_MONTHS : logs.RetentionDays.ONE_WEEK,
      functionName: `SRLinehandler-${stageName}`
    });

    // 👇 create a policy statement
    const InvokeFunctionPolicy = new iam.PolicyStatement({
      actions: ['lambda:InvokeFunction'],
      resources: ['*'],
    });

    // 👇 add the policy to the Function's role
    fn.role?.attachInlinePolicy(
      new iam.Policy(this, `Policy-SRhandler-${stageName}`, {
        statements: [InvokeFunctionPolicy],
      }),
    );

    // SpecRestApiを使ったAPIGatewayの作成
    const swaggerYaml = yaml.parse(
      fs.readFileSync("./rest_client/openapi.yaml").toString()
    );

    for (const path in swaggerYaml.paths) {
      for (const method in swaggerYaml.paths[path]) {
        swaggerYaml.paths[path][method]["x-amazon-apigateway-integration"] = {
          uri: `arn:${cdk.Aws.PARTITION}:apigateway:${cdk.Aws.REGION}:lambda:path/2015-03-31/functions/${fn.functionArn}/invocations`,
          passthroughBehavior: "when_no_match",
          httpMethod: "POST",
          type: "aws_proxy",
        };
      }
    }

    const apigw = new apigateway.SpecRestApi(this, `SRRestApi-${stageName}`, {
      apiDefinition: apigateway.ApiDefinition.fromInline(swaggerYaml),
      deployOptions: {
        stageName: stageName
      }
    });

    fn.addPermission("SRLambdaPermisson", {
      principal: new iam.ServicePrincipal("apigateway.amazonaws.com"),
      action: "lambda:InvokeFunction",
      sourceArn: apigw.arnForExecuteApi(),
    });

  }
}
