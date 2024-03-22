#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { HouseKeeperProStack } from "../lib/house-keeper-pro-cdk-stack";
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

const houseKeeperProStack = new HouseKeeperProStack(app, `HouseKeeperProStack-${stageName}`,{
  stageName: stageName,
});

cdk.Tags.of(houseKeeperProStack).add("Project", "house-keeper-pro")
cdk.Tags.of(houseKeeperProStack).add("Project_env", `house-keeper-pro-${stageName}`)
