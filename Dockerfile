
FROM ruby:3.2.2

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed gems specified in the Gemfile
RUN bundle install

# Make port 4000 available to the world outside this container
EXPOSE 4000

# Define environment variable
ENV JEKYLL_ENV=production

# Build your Jekyll site
RUN jekyll build

# Command to run your site using the default Jekyll server
CMD ["jekyll", "serve", "--host", "0.0.0.0", "--port", "4000"]
