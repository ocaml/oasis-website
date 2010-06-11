default: all

GENERATED_HTML=$(patsubst mkd/%.mkd,html/%.html,$(wildcard mkd/*.mkd))
GENERATED_IMG=html/oasis-badge.png html/powered-by-oasis.png html/logo.png 

all: $(GENERATED_HTML) $(GENERATED_IMG)

clean:
	-$(RM) $(GENERATED_HTML) $(GENERATED_IMG) logo-tmp.png

html/%.html: mkd/%.mkd html/part-header.html html/part-before-body.html html/part-after-body.html
	pandoc \
	  $(PANDOCFLAGS) \
	  -c default.css \
	  -H html/part-header.html \
	  -B html/part-before-body.html \
	  $< \
	  -A html/part-after-body.html \
          --email-obfuscation=references \
       	> $@

html/MANUAL.html: PANDOCFLAGS=--toc

html/oasis-badge.png: images/logo.svg images/background-badge.png
	inkscape -a 175:290:415:390 -w 24 -h 10 -e logo-tmp.png images/logo.svg
	composite -geometry +1+2 logo-tmp.png images/background-badge.png $@
	-$(RM) logo-tmp.png

html/%.png: images/%.svg
	inkscape $(INKSCAPEFLAGS) -e $@ $<

html/powered-by-oasis.png: INKSCAPEFLAGS=-w 128 -h 58

html/logo.png: INKSCAPEFLAGS=-w 160 -h 150

sync: all
	rsync -av -O --no-perms --delete html/ ssh.ocamlcore.org:/home/groups/oasis/htdocs/

#mkd/MANUAL.mkd: ../oasis/doc/MANUAL.mkd
#	cp $^ $@
