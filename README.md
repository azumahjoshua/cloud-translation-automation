# cloud-translation-automation

# create s3 bucket for the terraform state file before starting
aws s3 mb s3://terraform-bucket-20250207 --region us-east-1

# enable versioning on our s3 bucket 
aws s3api put-bucket-versioning --bucket terraform-bucket-20250207 --versioning-configuration Status=Enabled

# to start we need to initialize our terraform confguration files
terraform init 

# step 1 Create the s3 for the ouput and input json files
