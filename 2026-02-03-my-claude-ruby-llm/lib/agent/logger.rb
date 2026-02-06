# frozen_string_literal: true

require 'logger'
require 'fileutils'

module Agent
  # Logger for the agent
  module Logger
    @logger = nil

    def self.setup(log_dir: nil, log_level: ::Logger::INFO)
      log_dir ||= File.join(Dir.pwd, 'log')
      FileUtils.mkdir_p(log_dir)
      
      log_file = File.join(log_dir, 'agent.log')
      
      @logger = ::Logger.new(log_file, 'daily')
      @logger.level = log_level
      @logger.formatter = proc do |severity, datetime, progname, msg|
        "[#{datetime.strftime('%Y-%m-%d %H:%M:%S')}] #{severity}: #{msg}\n"
      end
      
      @logger
    end

    def self.logger
      @logger ||= setup
    end

    def self.info(message)
      logger.info(message)
    end

    def self.debug(message)
      logger.debug(message)
    end

    def self.warn(message)
      logger.warn(message)
    end

    def self.error(message)
      logger.error(message)
    end
  end
end
