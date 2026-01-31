#!/usr/bin/env ruby
# frozen_string_literal: true

require_relative 'lib/cli'

def main
  ClaudeCLI.run
end

exit main if __FILE__ == $PROGRAM_NAME
