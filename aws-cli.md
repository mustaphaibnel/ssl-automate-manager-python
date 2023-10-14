## Setting Up AWS CLI

Before using the SSL Automate Manager tool, you need to set up the AWS CLI. The tool interacts with Amazon S3 for backup purposes, so it's essential to configure AWS CLI with the necessary credentials. Follow the steps below to set it up:

### Prerequisites:

1. Ensure you have an AWS account. If not, sign up for one [here](https://aws.amazon.com/).
2. Install AWS CLI. If you haven't already, you can get it from [here](https://aws.amazon.com/cli/).

### Configuration Steps:

1. **Open a Terminal or Command Prompt**.

2. **Configure AWS CLI**:
   Run the following command:
   ```bash
   aws configure
   ```

3. **Input AWS Access Key ID**:
   You will be prompted to enter your `AWS Access Key ID`. This can be found in your AWS Management Console under `IAM` -> `Users` -> `YourUserName` -> `Security credentials`. If you haven't created an access key yet, you can do so by clicking on the `Create access key` button.

   ```bash
   AWS Access Key ID [None]: YOUR_ACCESS_KEY_ID
   ```

4. **Input AWS Secret Access Key**:
   Similarly, input the `AWS Secret Access Key` that was provided when you created your access key.

   ```bash
   AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
   ```

5. **Set Default Region**:
   Input the default region name. It should correspond to the AWS region you want to interact with. Example: `us-west-1`.

   ```bash
   Default region name [None]: YOUR_DEFAULT_REGION
   ```

6. **Set Default Output Format**:
   You can specify the output format for the AWS CLI. The options are `json`, `yaml`, `text`, and `table`. We recommend using `json`.

   ```bash
   Default output format [None]: json
   ```

7. **Completion**:
   After the steps above, your AWS CLI is now configured with the provided details. The tool will use these configurations to interact with your S3 bucket.

### Security Note:
Always keep your `AWS Access Key ID` and `AWS Secret Access Key` confidential. Avoid sharing these credentials or storing them in public places. If you believe your keys have been compromised, revoke them immediately in the AWS Management Console and generate a new pair.

