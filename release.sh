#!/bin/bash

version=$1
current_branch=$(git rev-parse --symbolic-full-name --abbrev-ref HEAD)
name=pricebot

# Check that script was run with argument
if [[ -z $1 ]]; then
  echo "Usage: ./release <VERSION>"
  exit 1
# Check that script was run from the intended branch
elif [[ $current_branch != "develop" ]]; then
  echo "Must be used from develop branch"
  exit 2
fi

# Update version number
sed -i "s/VERSION=.*/VERSION=$version/" .env

# Push updates and merge with master
git push origin develop
git checkout master
git merge develop
git push origin master

# Create and push tag for new version
git tag -a $version -m "Release $version"
git push origin $version

# Build and push new docker images
./build.sh
docker tag znibb/$name:latest znibb/$name:$version
docker push znibb/$name:$version
docker push znibb/$name:latest

# Exit gracefully
exit 0

