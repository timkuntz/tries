# frozen_string_literal: true

module Agent
  module Tools
    class FileMetadata < RubyLLM::Tool
      description 'Returns metadata of a file, including line-count, mtime'

      params do
        string(
          :path,
          description: 'Path to file. Must be a child of current directory.'
        )
      end

      attr_reader :working_dir

      def initialize(working_dir: nil, **)
        raise ArgumentError, 'working_dir is required' unless working_dir

        @working_dir = working_dir
      end

      def execute(path:, line_range_start: 0, line_range_end: nil, **params)
        return "The following params were passed but are not allowed: #{params.keys.join(',')}" if params.any?

        unless Paths.allowed?(working_dir, path)
          return "Path: #{path} not acceptable. Must be a child of directory: #{working_dir}."
        end

        workspace_path = Paths.relative_to_dir(working_dir, path)

        return 'File not found' unless File.exist?(workspace_path)

        {
          mtime: File.mtime(workspace_path),
          lines: File.foreach(workspace_path).count
        }
      end
    end
  end
end
