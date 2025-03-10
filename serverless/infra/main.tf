provider "aws" {
  region                   = "us-east-1"
  shared_credentials_files = ["~/.aws/credentials"]
  profile                  = "pwr" # this profile is used for the Learner Lab account
}

provider "archive" {}
