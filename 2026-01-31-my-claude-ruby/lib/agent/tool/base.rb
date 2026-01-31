# frozen_string_literal: true

module Agent
  module Tool
    # Base class for all tools providing common interface and introspection
    class Base
      # Get the tool name from the class name (EditFile -> "edit_file")
      def self.tool_name
        name.split('::').last
            .gsub(/([A-Z]+)([A-Z][a-z])/, '\1_\2')
            .gsub(/([a-z\d])([A-Z])/, '\1_\2')
            .downcase
      end

      # Extract parameters from the call method signature
      def self.parameters
        instance_method(:call).parameters
      end

      # Extract documentation from comments above the call method
      def self.documentation
        source_file = instance_method(:call).source_location[0]
        lines = File.readlines(source_file)
        method_line = lines.find_index { |line| line =~ /def call/ }

        # Scan backwards to find comment lines
        doc_lines = []
        (method_line - 1).downto(0) do |i|
          line = lines[i].strip
          break unless line.start_with?('#')

          doc_lines.unshift(line[1..].strip)
        end

        doc_lines.first || 'No documentation available'
      end

      # Class method wrapper that creates instance and calls it
      def self.call(**args)
        new.call(**args)
      end

      # Instance method to be implemented by subclasses
      def call(**_args)
        raise NotImplementedError, "#{self.class} must implement #call"
      end
    end
  end
end
