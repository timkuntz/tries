# Coding Agent with RubyLLM

This is a simple coding assistant build using RubyLLM.

## Setup

```bash
bundle install
```

## Running the Coding Agent

The agent is hardcoded to use AWS Bedrock so you will need to setup the required environment variables for AWS credentials and region.

```bash
awsume some-profile
```

Then run:

```bash
./agent.rb
```

## Project Structure

- `lib/` - Source code
