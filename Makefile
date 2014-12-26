VERSION := 0.0.1

all: clean build deb

build:
	mkdir -p packaging/root/usr/lib/apt/methods/
	cp github.py packaging/root/usr/lib/apt/methods/github
	chmod +x packaging/root/usr/lib/apt/methods/github

clean:
	rm -rf packaging

test:
	unit2 -fv

deb:
	fpm -s dir -t deb -n apt-transport-github \
	    -v $(VERSION) \
	    -p packaging/apt-transport-github_VERSION_ARCH.deb \
		--deb-priority optional --category admin \
		--force \
		--description "Fetch Debian packages via Github release API" \
		-m "Janez Troha <dz0ny@ubuntu.si>" \
		--license "MIT" \
		-d "python-requests" \
		--deb-compression bzip2 \
		-a all \
		packaging/root/=/

install:
	sudo dpkg -i packaging/apt-transport-github_$(VERSION)_amd64.deb

deploy:
	-github-release delete -u dz0ny -r apt-transport-github -t v$(VERSION)
	-github-release delete -u dz0ny -r apt-transport-github -t latest
	github-release release -u dz0ny -r apt-transport-github -t v$(VERSION)
	github-release release -u dz0ny -r apt-transport-github -t latest
	github-release upload -u dz0ny -r apt-transport-github -t v$(VERSION) -f packaging/apt-transport-*.deb -n apt-transport-github_$(VERSION)_all.deb
	github-release upload -u dz0ny -r apt-transport-github -t latest -f packaging/apt-transport-*.deb -n apt-transport-github_$(VERSION)_all.deb