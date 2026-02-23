source "https://rubygems.org"

# GitHub Pages gem pins Jekyll + whitelisted plugins to safe versions.
# Remove it and use the gems below directly if deploying via GitHub Actions.
gem "github-pages", group: :jekyll_plugins

group :jekyll_plugins do
  gem "jekyll-feed"
  gem "jekyll-seo-tag"
  gem "jekyll-sitemap"
  gem "jekyll-paginate"
  gem "jekyll-remote-theme"
end

# Windows / JRuby helpers
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

gem "wdm", "~> 0.1", platforms: :mingw, :x64_mingw, :mswin
gem "http_parser.rb", "~> 0.6.0", platforms: :jruby
