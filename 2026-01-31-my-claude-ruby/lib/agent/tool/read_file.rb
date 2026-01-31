# frozen_string_literal: true

require_relative 'base'
require 'pathname'

module Agent
  module Tool
    # LLM tool that reads the content of a file.
    class ReadFile < Base
      # Gets the full content of a file provided by the user.
      def call(filename:)
        full_path = Pathname.new(filename).expand_path
        puts full_path
        content = File.read(full_path)
        {
          file_path: full_path.to_s,
          content: content
        }
      end
    end
  end
end
