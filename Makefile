INKSCAPE=inkscape
COMPOSITE=composite
PANDOC=pandoc
TAR=tar

# Determine if we can scrape host.
ONLINE := $(shell (ping -c 1 forge.ocamlcore.org > /dev/null 2>&1 && echo true) || echo false)

default: all

include Makefile.scrape

#
# Convert .mkd to .html
#

GENERATED_MKD=$(patsubst %.mkd.tmpl,%.mkd,$(wildcard mkd/*.mkd.tmpl))

GENERATED_HTML=$(patsubst mkd/%.mkd,html/%.html, \
								$(wildcard mkd/*.mkd) $(GENERATED_MKD))
GENERATED_HTML+=$(foreach version,$(OASIS_DOC_VERSIONS),html/MANUAL-$(version).html)
GENERATED_HTML+=html/MANUAL.html
GENERATED_IMG=html/oasis-badge.png html/powered-by-oasis.png html/logo.png

all: $(GENERATED_HTML) $(GENERATED_IMG)
	echo $(GENERATED_HTML)

.PHONY: all

clean::
	-$(RM) $(GENERATED_MKD) $(GENERATED_HTML) $(GENERATED_IMG) logo-tmp.png

.PHONY: clean

html/MANUAL-%.html: PANDOCFLAGS=--toc

html/%.html: mkd/%.mkd mkd/part-header.html mkd/part-before-body.html mkd/part-after-body.html
	$(PANDOC) $(PANDOCFLAGS) \
	  -c default.css \
	  -H mkd/part-header.html \
	  -B mkd/part-before-body.html \
	  $(filter %.mkd,$^) \
	  -A mkd/part-after-body.html \
	  --email-obfuscation=references \
	  --output $@

html/MANUAL.html: html/MANUAL-$(OASIS_LATEST_VERSION).html
	cp $< $@

#
# Convert .mkd.tmpl into .mkd.
#

%.mkd: %.mkd.tmpl scrape.json
	./template.py $(foreach file,$(filter %.json,$^),--data $(file) ) \
		--input $(filter %.mkd.tmpl,$^) \
		--output $@

#
# Extract tarballs.
#

cache/oasis-doc-%.dir: cache/oasis-doc-%.tar.gz
	$(TAR) xzf $^ -C cache
	mv cache/oasis-doc-$* $@

mkd/MANUAL-%.mkd: cache/oasis-doc-%.dir
	cp $</doc/MANUAL.mkd $@

clean::
	-$(RM) -r doc/oasis-doc-*.dir

#
# Image generation.
#
# Convert .svg into .png.
#

html/oasis-badge.png: images/logo.svg images/background-badge.png
	$(INKSCAPE) -a 175:290:415:390 -w 24 -h 10 -e logo-tmp.png images/logo.svg
	$(COMPOSITE) -geometry +1+2 logo-tmp.png images/background-badge.png $@
	-$(RM) logo-tmp.png

html/%.png: images/%.svg
	inkscape $(INKSCAPEFLAGS) -e $@ $<

html/powered-by-oasis.png: INKSCAPEFLAGS=-w 128 -h 58

html/logo.png: INKSCAPEFLAGS=-w 160 -h 150

#
# Scraping files page of the forge OASIS project.
#
# Extract data from the forge project.
#

Makefile.scrape: scrape.sh
	./scrape.sh

clean::
	if $(ONLINE) ; then -$(RM) -r html/oasis-doc-* scrape-include; fi

distclean::
	-$(RM) -R cache

#
# Deployment target.
#
# Deploy generated website to oasis.forge.o.o.
#

deploy: all
	rsync -av -O --no-perms --delete \
		--exclude oasis-db/server-dev/*.log \
		--exclude oasis-db/server-dev/incoming \
		--exclude oasis-db/server-dev/dist html/ \
		ssh.ocamlcore.org:/home/groups/oasis/htdocs/

.PHONY: deploy
