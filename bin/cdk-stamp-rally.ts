#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { StampRallyStack } from "../lib/stamp-rally-cdk-stack";
import { ENVS } from "../lib/env";

const app = new cdk.App();

// 環境の指定 -c environment=('dev'||'prod')
const argContext = 'environment';
const stageName = app.node.tryGetContext(argContext);

if(!Object.values(ENVS).includes(stageName)){
  throw new Error(
    `環境が指定されていないまたは、適当な環境が指定されていません -> env_name:${stageName}`
  );
}

const stampRallyStack = new StampRallyStack(app, `StampRallyStack-${stageName}`,{
  stageName: stageName,
});

cdk.Tags.of(stampRallyStack).add("Project", "stamp-rally")
cdk.Tags.of(stampRallyStack).add("Project_env", `stamp-rally-${stageName}`)
