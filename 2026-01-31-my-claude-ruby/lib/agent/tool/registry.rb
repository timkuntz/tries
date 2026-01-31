# frozen_string_literal: true

require_relative 'base'

module Agent
  module Tool
    # Registry for discovering and managing tool classes
    class Registry
      class << self
        # Get string representation of a tool for prompts
        def tool_description(tool_name)
          tool_info = all[tool_name]
          doc = tool_info[:documentation]
          params = tool_info[:parameters].map { |_type, name| "#{name}: ..." }.join(', ')

          <<~TOOL_STR
            Name: #{tool_name}
            Description: #{doc}
            Signature: (#{params})
          TOOL_STR
        end

        # Get all tool names
        def tool_names
          all.keys
        end

        def tool(name)
          all[name][:callable]
        end

        private

        # Build registry from all Tool::Base subclasses
        def build
          registry = {}
          Base.subclasses.each do |tool_class|
            registry[tool_class.tool_name] = {
              callable: tool_class,
              documentation: tool_class.documentation,
              parameters: tool_class.parameters
            }
          end
          registry
        end

        # Get memoized registry
        def all
          @all ||= build
        end

        # Reset registry (useful for testing)
        def reset!
          @all = nil
        end
      end
    end
  end
end
