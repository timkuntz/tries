#!/usr/bin/env ruby
# frozen_string_literal: true

require 'zeitwerk'

loader = Zeitwerk::Loader.new
loader.push_dir('lib')
loader.enable_reloading
loader.setup # ready!
loader.reload

def main
  Agent::Cli.run
end

exit main if __FILE__ == $PROGRAM_NAME
