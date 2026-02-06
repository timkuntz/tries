# frozen_string_literal: true

module Agent
  # Library of tools the agent can use.
  module Tools
    NAMES = {
      read_file: ReadFile,
      edit_file: EditFile,
      grep: Grep,
      file_metadata: FileMetadata,
      dir_glob: DirGlob,
      run_rails_test: RunRailsTest
    }.freeze

    def self.all(**params)
      NAMES.values.map { _1.new(**params) }
    end

    def self.resolve(*names, **params)
      names.flatten.map { NAMES.fetch(_1.to_sym).new(**params) }
    end
  end
end
