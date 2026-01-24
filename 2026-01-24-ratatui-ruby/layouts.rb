require 'ratatui_ruby'

# 1. Initialize the terminal, start the run loop, and ensure the terminal is restored.
RatatuiRuby.run do |tui|
  loop do
    tui.draw do |frame|
      # 1. Split the screen
      top, bottom = tui.layout_split(
        frame.area,
        direction: :vertical,
        constraints: [
          tui.constraint_percentage(75),
          tui.constraint_percentage(25),
        ]
      )

      # 2. Render Top Widget
      frame.render_widget(
        tui.paragraph(
          text: "Hello, Ratatui!",
          alignment: :center,
          block: tui.block(title: "Content", borders: [:all], border_style: { fg: "cyan" })
        ),
        top
      )

      # 3. Render Bottom Widget with Styled Text
      # We use a Line of Spans to style specific characters
      text_line = tui.text_line(
        spans: [
          tui.text_span(content: "Press '"),
          tui.text_span(
            content: "q",
            style: tui.style(modifiers: [:bold, :underlined])
          ),
          tui.text_span(content: "' to quit."),
        ],
        alignment: :center
      )

      frame.render_widget(
        tui.paragraph(
          text: text_line,
          block: tui.block(title: "Controls", borders: [:all])
        ),
        bottom
      )
    end

    case tui.poll_event
    in { type: :key, code: "q" }
      break
    else
      # Ignore other events
    end
  end
end
