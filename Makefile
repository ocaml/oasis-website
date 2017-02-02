INKSCAPE=inkscape
COMPOSITE=composite
PANDOC=pandoc
TAR=tar
CURL=curl
FAB=fab
LINKCHECKER=linkchecker

# Determine if we can scrape host.
ONLINE := $(shell (ping -c 1 forge.ocamlcore.org > /dev/null 2>&1 && echo true) || echo false)

# HTML page to scrape for data.
FORGE_PAGE := "http://forge.ocamlcore.org/frs/?group_id=54"

# Dev documetation link.
DEV_DOC_URL := "file:///$(shell pwd)/oasis-doc-dev.tar.gz"

default: all

include Makefile.scrape

#
# Convert .mkd to .html
#

# mkd files generated from template.
GENERATED_MKD=$(patsubst %.mkd.tmpl,%.mkd,$(wildcard mkd/*.mkd.tmpl))
ALL_MKD=$(wildcard mkd/*.mkd) $(GENERATED_MKD)

# Expected HTML files.
GENERATED_HTML=$(patsubst mkd/%.mkd,html/%.html,$(ALL_MKD))
GENERATED_HTML+=$(foreach version,$(OASIS_DOC_VERSIONS),html/MANUAL-$(version).html)
GENERATED_HTML+=html/MANUAL.html

# Directories created during the process.
GENERATED_DIR+=$(foreach version,$(OASIS_DOC_VERSIONS),html/api-oasis-$(version))
GENERATED_DIR+=html/api-oasis

# Images generated.
GENERATED_IMG=html/oasis-badge.png html/powered-by-oasis.png html/logo.png

# Generated files.
GENERATED_FILE=Makefile.scrape html/robots.txt

all: $(GENERATED_HTML) $(GENERATED_IMG) $(foreach d,$(GENERATED_DIR),$d/stamp) html/robots.txt marknonlatest

.PHONY: all

clean::
	-$(RM) \
			$(GENERATED_FILE) \
			$(GENERATED_MKD) \
			$(GENERATED_HTML) \
			$(GENERATED_IMG) \
			logo-tmp.png
	-$(RM) -r $(GENERATED_DIR)

distclean:: clean
	-$(RM) -R cache

.PHONY: clean distclean

html/MANUAL-%.html: PANDOCFLAGS=--toc
html/faq.html: PANDOCFLAGS=--toc

html/%.html: mkd/%.mkd mkd/part-header.html mkd/part-before-body.html mkd/part-after-body.html
	$(PANDOC) $(PANDOCFLAGS) \
	  -c default.css \
	  -H mkd/part-header.html \
	  -B mkd/part-before-body.html \
	  $(filter %.mkd,$^) \
	  -A mkd/part-after-body.html \
	  --email-obfuscation=references \
	  --output $@

# Default linking to stable version.
html/MANUAL.html: html/MANUAL-$(OASIS_LATEST_VERSION).html
	cp $< $@
html/api-oasis/stamp: html/api-oasis-$(OASIS_LATEST_VERSION)/stamp
	cp -R $$(dirname $<) $$(dirname $@)

#
# Convert template file.
#

TEMPLATE_PY= ./template.py --cache_dir "$(CURDIR)/cache" \
						   --forge_page $(FORGE_PAGE) --online $(ONLINE) \
							 --log=INFO

%: %.tmpl
	$(TEMPLATE_PY) --input "$<" --output "$@"

mkd/%: mkd/%.tmpl
	$(TEMPLATE_PY) --input "$<" --output "$@"

html/robots.txt: tmpl/robots.txt.tmpl
	$(TEMPLATE_PY) --input "$<" --output "$@"

#
# Download tarballs.
#

cache/oasis-doc-dev.tar.gz: URL=$(DEV_DOC_URL)

cache/oasis-doc-%.tar.gz:
	$(CURL) -o $@ $(URL)

#
# Extract tarballs.
#

cache/oasis-doc-%.dir/stamp: cache/oasis-doc-%.tar.gz
	$(TAR) xzf $^ -C cache
	mv cache/oasis-doc-$* $$(dirname $@)
	touch $@

mkd/MANUAL-0.3.0.mkd: cache/oasis-doc-0.3.0.dir/stamp
	cp $$(dirname $<)/doc/MANUAL.mkd $@
	sed -i -e 's,http://omake.metaprl.org,http://omake.metaprl.org/index.html,' $@
	sed -i -e 's,http://ocaml.info/home/ocaml_sources.html,http://www.ocaml.info/software.html#build_tools,' $@

mkd/MANUAL-%.mkd: cache/oasis-doc-%.dir/stamp
	cp $$(dirname $<)/doc/MANUAL.mkd $@

html/api-oasis-%/stamp: cache/oasis-doc-%.dir/stamp
	cp -R $$(dirname $<)/api-oasis $$(dirname $@)
	touch $@

clean::
	-$(RM) -r cache/oasis-doc-*.dir

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
# Mark the documentation for version which are not the latest.
#

MARKNONLATESTARGS=--text 'You are viewing a development version of the library.'

html/api-oasis-dev/marknonlatest.stamp: MARKNONLATESTARGS=--text 'You are viewing a development version of the library.'
html/api-oasis-$(OASIS_LATEST_VERSION)/marknonlatest.stamp: MARKNONLATESTARGS=--unset

html/api-oasis-%/marknonlatest.stamp: html/api-oasis-%/stamp
	./marknonlatest.py $$(dirname $@)/*.html $(MARKNONLATESTARGS) --link '../api-oasis/index.html'
	touch $@

marknonlatest: $(GENERATED_HTML) $(foreach version,$(OASIS_DOC_VERSIONS),html/api-oasis-$(version)/marknonlatest.stamp)
	./marknonlatest.py html/MANUAL-*.html \
		--text 'You are not viewing the latest version of the manual.' \
		--link 'MANUAL.html'
	./marknonlatest.py html/MANUAL-dev.html \
		--text 'You are viewing a development version of the manual.' \
		--link 'MANUAL.html'
	./marknonlatest.py html/MANUAL-$(OASIS_LATEST_VERSION).html --unset

.PHONY: marknonlatest

#
# Deployment target.
#
# Deploy generated website to oasis.forge.o.o.
#

deploy:
	$(FAB) deploy

rollback:
	$(FAB) rollback

.PHONY: deploy rollback


#
# Test quality of the website.
#

test:
	linkchecker $(CURDIR)/html/index.html \
		--ignore-url=^http://d1.scribdassets.com \
		--ignore-url=^mailto: \
		--ignore-url=^https://s3.amazonaws.com \
		--ignore-url=^http://ocsigen.org
