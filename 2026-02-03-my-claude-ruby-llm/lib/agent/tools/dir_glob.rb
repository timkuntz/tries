# frozen_string_literal: true

module Agent
  module Tools
    class DirGlob < RubyLLM::Tool
      description('Find files in a directory using a ruby-compatible glob pattern.')

      params do
        string(
          :glob_pattern,
          description: 'Only returns children paths of the current directory'
        )
      end

      attr_reader :working_dir

      def initialize(working_dir: nil, **)
        raise ArgumentError, 'working_dir is required' unless working_dir

        @working_dir = working_dir
      end

      def execute(glob_pattern:, **params)
        return "The following params were passed but are not allowed: #{params.keys.join(',')}" if params.any?

        unless Paths.allowed?(working_dir, glob_pattern)
          return "Path: #{glob_pattern} not acceptable. Must be a child of directory: #{working_dir}."
        end

        results = Dir
                  .glob(File.join(working_dir, glob_pattern))
                  .select { Paths.allowed?(working_dir, _1) }

        warning = (
          "Returning 30 of #{results.count} results" if results.count > 30
        )

        [warning, results.take(30).to_json].compact.join("\n")
      end
    end
  end
end
