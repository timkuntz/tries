# frozen_string_literal: true

require 'json'
require 'pathname'
require 'ruby_llm'

module Agent
  # CLI for coding assistant
  module Cli
    # Terminal colors
    YOU_COLOR = "\u001b[94m"
    ASSISTANT_COLOR = "\u001b[93m"
    RESET_COLOR = "\u001b[0m"

    # System prompt
    def self.full_system_prompt
      <<~PROMPT
        You are a coding assistant whose goal it is to help us solve coding tasks.
      PROMPT
    end

    def self.user_prompt
      print "#{YOU_COLOR}You:#{RESET_COLOR} "
      gets.strip!
    end

    def self.llm_response(response, conversation)
      puts "#{ASSISTANT_COLOR}Assistant:#{RESET_COLOR} #{response}"
      conversation << {
        role: 'assistant',
        content: response
      }
    end

    def self.initialize_chat
      chat = RubyLLM.chat
      chat.with_instructions(full_system_prompt)

      working_dir = ARGV[0] || Dir.pwd
      puts "Using working directory: #{working_dir}"

      tools = Tools.all(working_dir: working_dir)

      puts "Initialized tools: #{tools.map(&:class).join(', ')}"
      chat.with_tools(*tools)
    end

    # Main agent loop
    def self.run_coding_agent_loop
      chat = initialize_chat

      loop do
        query = user_prompt
        break if %w[exit quit].include? query.downcase

        response = chat.ask(query)
        puts "#{ASSISTANT_COLOR}Assistant:#{RESET_COLOR} #{response.content}"
      rescue Interrupt, EOFError
        break
      end
    end

    # Main entry point
    def self.run
      RubyLLM.configure do |config|
        config.bedrock_api_key = ENV.fetch('AWS_ACCESS_KEY_ID')
        config.bedrock_secret_key = ENV.fetch('AWS_SECRET_ACCESS_KEY')
        config.bedrock_session_token = ENV.fetch('AWS_SESSION_TOKEN')
        config.bedrock_region = ENV.fetch('AWS_REGION', 'us-west-2')
        config.default_model = ENV.fetch('LLM_MODEL', 'us.anthropic.claude-sonnet-4-5-20250929-v1:0')
      end
      run_coding_agent_loop
      0
    end
  end
end
