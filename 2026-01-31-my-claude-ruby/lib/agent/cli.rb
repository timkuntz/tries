# frozen_string_literal: true

require 'json'
require 'pathname'
require 'openai'

# Auto-load all tool classes
Dir[File.join(__dir__, 'tool', '*.rb')].each { |file| require file }

module Agent
  # CLI for coding assistant
  module CLI
    # Terminal colors
    YOU_COLOR = "\u001b[94m"
    ASSISTANT_COLOR = "\u001b[93m"
    RESET_COLOR = "\u001b[0m"

    # System prompt
    def self.full_system_prompt
      tool_str_repr = Tool::Registry.tool_names.map do |tool_name|
        "TOOL\n====\n#{Tool::Registry.tool_description(tool_name)}#{'=' * 15}"
      end.join("\n")

      <<~PROMPT
        You are a coding assistant whose goal it is to help us solve coding tasks.
        You have access to a series of tools you can execute. Here are the tools you can execute:

        #{tool_str_repr}

        When you want to use a tool, reply with exactly one line in the format: 'tool: TOOL_NAME({{JSON_ARGS}})' and nothing else.
        Use compact single-line JSON with double quotes. After receiving a tool_result(...) message, continue the task.
        If no tool is needed, respond normally.
      PROMPT

      # Interesting that these additional instructions break how the LLM calls the "list_files" tool.
      # When referencing files, if a path is not specified and is not absolute,
      # assume it is relative to the current working directory.
      # Use the path "./" to refer to the current working directory."
      # If you need to check if a file exists, use the list_files tool.
    end

    # Extract tool invocations from text
    def self.extract_tool_invocations(text)
      invocations = []
      pattern = /^tool: (.*?)\((.*)\)/
      text.each_line do |line|
        next unless (match = pattern.match(line.strip))

        name, json_str = match.captures.map(&:strip)
        args = JSON.parse(json_str, symbolize_names: true)
        invocations << [name, args]
      end
      invocations
    end

    def self.messages(conversation)
      conversation.map do |msg|
        {
          role: msg[:role],
          content: msg[:content]
        }
      end
    end

    # Execute LLM call
    def self.execute_llm_call(openai_client, conversation)
      response = openai_client.chat(
        parameters: {
          model: 'gpt-4o',
          max_tokens: 2000,
          messages: messages(conversation)
        }
      )
      response.dig('choices', 0, 'message', 'content')
    end

    def self.user_prompt(conversation)
      print "#{YOU_COLOR}You:#{RESET_COLOR} "
      user_input = gets
      exit(0) if user_input.nil?

      conversation << {
        role: 'user',
        content: user_input.strip
      }
    end

    def self.llm_response(response, conversation)
      puts "#{ASSISTANT_COLOR}Assistant:#{RESET_COLOR} #{response}"
      conversation << {
        role: 'assistant',
        content: response
      }
    end

    def self.invoke_tools(tools, conversation)
      tools.each do |name, args|
        tool = Tool::Registry.tool(name)
        resp = tool.call(**args)
        conversation << {
          role: 'user',
          content: "tool_result(#{JSON.generate(resp)})"
        }
      end
    end

    # Main agent loop
    def self.run_coding_agent_loop(openai_client)
      conversation = [{
        role: 'system',
        content: full_system_prompt
      }]

      loop do
        user_prompt(conversation)

        loop do
          assistant_response = execute_llm_call(openai_client, conversation)
          tool_invocations = extract_tool_invocations(assistant_response)

          if tool_invocations.empty?
            llm_response(assistant_response, conversation)
            break
          end
          invoke_tools(tool_invocations, conversation)
        end
      rescue Interrupt, EOFError
        break
      end
    end

    # Main entry point
    def self.run
      openai_client = OpenAI::Client.new(access_token: ENV['OPENAI_API_KEY'])
      run_coding_agent_loop(openai_client)
      0
    end
  end
end
