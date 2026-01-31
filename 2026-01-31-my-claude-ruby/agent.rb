#!/usr/bin/env ruby
# frozen_string_literal: true

require_relative 'lib/agent/cli'

def main
  Agent::CLI.run
end

exit main if __FILE__ == $PROGRAM_NAME
