INKSCAPE="inkscape"
COMPOSITE="composite"
PANDOC="pandoc"

default: all

include Makefile.scrape
include Makefile.mkd

#
# Convert .mkd to .html
#

GENERATED_HTML=$(patsubst mkd/%.mkd,html/%.html,$(wildcard mkd/*.mkd))
GENERATED_HTML+=$(patsubst %,html/MANUAL-%.html,$(OASIS_DOC_VERSIONS))
GENERATED_IMG=html/oasis-badge.png html/powered-by-oasis.png html/logo.png

all: $(GENERATED_HTML) $(GENERATED_IMG)
	echo $(GENERATED_HTML)

.PHONY: all

clean::
	-$(RM) $(GENERATED_HTML) $(GENERATED_IMG) logo-tmp.png

.PHONY: clean

html/%.html: html/part-header.html html/part-before-body.html html/part-after-body.html
	$(PANDOC) \
	  $(PANDOCFLAGS) \
	  -c default.css \
	  -H html/part-header.html \
	  -B html/part-before-body.html \
	  $(filter %.mkd,$^) \
	  -A html/part-after-body.html \
    --email-obfuscation=references > $@

html/MANUAL-%.html: PANDOCFLAGS=--toc

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
	-$(RM) -r html/oasis-doc-*
	-$(RM) scrape-include

distclean::
	-$(RM) -R cache

#
# Extract mkd dependencies
#

Makefile.mkd:
	ls -1 mkd/*.mkd | sed 's,mkd/\(.*\)\.mkd,html/\1.html: \0,' > $@

clean::
	-$(RM) Makefile.mkd

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
