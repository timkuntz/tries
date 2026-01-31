# frozen_string_literal: true

require 'json'
require 'pathname'
require 'openai'

# CLI for coding assistant
module ClaudeCLI
  # Terminal colors
  YOU_COLOR = "\u001b[94m"
  ASSISTANT_COLOR = "\u001b[93m"
  RESET_COLOR = "\u001b[0m"

  # Resolve absolute path from string
  def self.resolve_abs_path(path_str)
    path = Pathname.new(path_str).expand_path
    path.absolute? ? path : (Pathname.pwd / path).realpath
  end

  # Tool: Read file
  def self.read_file_tool(filename:)
    full_path = resolve_abs_path(filename)
    puts full_path
    content = File.read(full_path)
    {
      file_path: full_path.to_s,
      content: content
    }
  end

  # Tool: List files
  def self.list_files_tool(path:)
    full_path = resolve_abs_path(path)
    all_files = full_path.children.map do |item|
      {
        filename: item.basename.to_s,
        type: item.file? ? 'file' : 'dir'
      }
    end
    {
      path: full_path.to_s,
      files: all_files
    }
  end

  # Tool: Edit file
  def self.edit_file_tool(path:, old_str:, new_str:)
    full_path = resolve_abs_path(path)

    if old_str.empty?
      File.write(full_path, new_str)
      return {
        path: full_path.to_s,
        action: 'created_file'
      }
    end

    original = File.read(full_path)
    unless original.include?(old_str)
      return {
        path: full_path.to_s,
        action: 'old_str not found'
      }
    end

    edited = original.sub(old_str, new_str)
    File.write(full_path, edited)
    {
      path: full_path.to_s,
      action: 'edited'
    }
  end

  # Tool registry
  TOOL_REGISTRY = {
    'read_file' => method(:read_file_tool),
    'list_files' => method(:list_files_tool),
    'edit_file' => method(:edit_file_tool)
  }.freeze

  # Get tool string representation
  def self.get_tool_str_representation(tool_name)
    tool_method = TOOL_REGISTRY[tool_name]
    params = tool_method.parameters.map { |type, name| "#{name}: ..." }.join(', ')

    doc = case tool_name
          when 'read_file'
            'Gets the full content of a file provided by the user.'
          when 'list_files'
            'Lists the files in a directory provided by the user.'
          when 'edit_file'
            'Replaces first occurrence of old_str with new_str in file. If old_str is empty, create/overwrite file with new_str.'
          end

    "
  Name: #{tool_name}
  Description: #{doc}
  Signature: (#{params})
  "
  end

  # System prompt
  def self.get_full_system_prompt
    tool_str_repr = TOOL_REGISTRY.keys.map do |tool_name|
      "TOOL\n===" + get_tool_str_representation(tool_name) + "\n" + ('=' * 15)
    end.join("\n")

    <<~PROMPT
      You are a coding assistant whose goal it is to help us solve coding tasks.
      You have access to a series of tools you can execute. Here are the tools you can execute:

      #{tool_str_repr}

      When you want to use a tool, reply with exactly one line in the format: 'tool: TOOL_NAME({{JSON_ARGS}})' and nothing else.
      Use compact single-line JSON with double quotes. After receiving a tool_result(...) message, continue the task.
      If no tool is needed, respond normally.
    PROMPT
  end

  # Extract tool invocations from text
  def self.extract_tool_invocations(text)
    invocations = []
    text.each_line do |raw_line|
      line = raw_line.strip
      next unless line.start_with?('tool:')

      begin
        after = line[5..].strip
        name, rest = after.split('(', 2)
        name = name.strip
        next unless rest&.end_with?(')')

        json_str = rest[0...-1].strip
        args = JSON.parse(json_str, symbolize_names: true)
        invocations << [name, args]
      rescue StandardError
        next
      end
    end
    invocations
  end

  # Execute LLM call
  def self.execute_llm_call(openai_client, conversation)
    messages = conversation.map do |msg|
      { role: msg[:role], content: msg[:content] }
    end

    response = openai_client.chat(
      parameters: {
        model: 'gpt-4o',
        max_tokens: 2000,
        messages: messages
      }
    )

    response.dig('choices', 0, 'message', 'content')
  end

  # Main agent loop
  def self.run_coding_agent_loop(openai_client)
    puts get_full_system_prompt

    conversation = [{
      role: 'system',
      content: get_full_system_prompt
    }]

    loop do
      print "#{YOU_COLOR}You:#{RESET_COLOR} "
      user_input = gets
      break if user_input.nil?

      user_input = user_input.strip
      conversation << {
        role: 'user',
        content: user_input
      }

      loop do
        assistant_response = execute_llm_call(openai_client, conversation)
        tool_invocations = extract_tool_invocations(assistant_response)

        if tool_invocations.empty?
          puts "#{ASSISTANT_COLOR}Assistant:#{RESET_COLOR} #{assistant_response}"
          conversation << {
            role: 'assistant',
            content: assistant_response
          }
          break
        end

        tool_invocations.each do |name, args|
          tool = TOOL_REGISTRY[name]
          puts "#{name} #{args}"
          resp = tool.call(**args)
          conversation << {
            role: 'user',
            content: "tool_result(#{JSON.generate(resp)})"
          }
        end
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
