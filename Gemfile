source "https://rubygems.org"

# Deployed via GitHub Actions — no github-pages gem needed.
# This lets us use Jekyll 4 + Liquid 5, which Chirpy requires.
gem "jekyll", "~> 4.3"
gem "jekyll-theme-chirpy", "~> 7.0"

group :jekyll_plugins do
  gem "jekyll-seo-tag"
  gem "jekyll-sitemap"
  gem "jekyll-paginate"
  gem "jekyll-archives"
end

# Windows / JRuby helpers
platforms :windows, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

gem "wdm", "~> 0.1", platforms: [:windows]
gem "http_parser.rb", "~> 0.6.0", platforms: [:jruby]
