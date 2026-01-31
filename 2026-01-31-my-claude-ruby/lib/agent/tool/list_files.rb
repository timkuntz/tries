# frozen_string_literal: true

require_relative 'base'
require 'pathname'

module Agent
  module Tool
    # LLM tool that lists files in a directory.
    class ListFiles < Base
      # Lists the files in a directory provided by the user.
      def call(path:)
        full_path = Pathname.new(path).expand_path
        {
          path: full_path.to_s,
          files: children(full_path)
        }
      end

      private

      def children(pathname)
        pathname.children.map do |item|
          {
            filename: item.basename.to_s,
            type: item.file? ? 'file' : 'dir'
          }
        end
      end
    end
  end
end
