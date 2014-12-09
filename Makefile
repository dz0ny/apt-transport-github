VERSION := 0.0.1

all: clean build deb

build:
	mkdir -p packaging/root/usr/lib/apt/methods/
	cp github.py packaging/root/usr/lib/apt/methods/gihub
	chmod +x packaging/root/usr/lib/apt/methods/gihub

clean:
	rm -rf packaging

deb:
	fpm -s dir -t deb -n apt-transport-github -v $(VERSION) -p packaging/apt-transport-github_amd64.deb \
		--deb-priority optional --category admin \
		--force \
		--description "Fetch Debian packages via Github release API" \
		-m "Janez Troha <dz0ny@ubuntu.si>" \
		--license "MIT" \
		--deb-compression bzip2 \
		-a amd64 \
		packaging/root/=/

deploy:
	-github-release delete -u dz0ny -r apt-transport-github -t v$(VERSION)
	-github-release delete -u dz0ny -r apt-transport-github -t latest
	github-release release -u dz0ny -r apt-transport-github -t v$(VERSION)
	github-release release -u dz0ny -r apt-transport-github -t latest
	github-release upload -u dz0ny -r apt-transport-github -t v$(VERSION) -f packaging/apt-transport-github_amd64.deb -n apt-transport-github_amd64.deb
	github-release upload -u dz0ny -r apt-transport-github -t latest -f packaging/apt-transport-github_amd64.deb -n apt-transport-github_amd64.deb