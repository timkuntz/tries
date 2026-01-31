# frozen_string_literal: true

require_relative 'base'
require 'pathname'

module Agent
  module Tool
    class EditFile < Base
      # Replaces first occurrence of old_str with new_str in file. If old_str is empty, create/overwrite.
      def call(path:, old_str:, new_str:)
        full_path = Pathname.new(path).expand_path

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
    end
  end
end
