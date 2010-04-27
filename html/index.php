<?php

$domain=ereg_replace('[^\.]*\.(.*)$','\1',$_SERVER['HTTP_HOST']);
$group_name=ereg_replace('([^\.]*)\..*$','\1',$_SERVER['HTTP_HOST']);
$group_id=54;

echo '<?xml version="1.0" encoding="UTF-8"?>';
?>
<!DOCTYPE html
	PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <title>About OASIS</title>
    <link href="default.css" rel="stylesheet" type="text/css"/>
<?php include "part-header.html"; ?>
  </head>

  <body>

<?php include "part-before-body.html"; ?>
      
      <h2>What is OASIS?</h2>

      <p>OASIS can integrate configure, build and install systems in their projects. It helps to 
      create standard entry points in the source code build system and allows external tools to analyse
      projects easily.</p>

      <p>It is inspired by <a href="http://www.haskell.org/cabal">Cabal</a> which is the same kind of tool for
      <a href="http://www.haskell.org">Haskell</a>.</p>

      <p>OASIS was created with <a href="http://brion.inria.fr/gallium/index.php/Ocamlbuild">OCamlbuild</a> in mind.
      So there are probably some features/bugs that are the same.</p>

      <p>Features:</p>

      <ul>
      <li>OCamlbuild support (<a href="MANUAL.html#plugin-ocamlbuild">see here</a>)</li>
      <li>Standard files auto-generation (see here <a href="MANUAL.html#plugin-devfiles">1</a>,
      <a href="MANUAL.html#plugin-meta">2</a>, <a href="MANUAL.html#plugin-stdfiles">3</a>)</li>
      </ul>

      <p>Planned features:</p>

      <ul>
      <li><a href="http://ocaml-autoconf.forge.ocamlcore.org">OCaml autoconf</a></li>
      <li><a href="http://omake.metaprl.org">OMake</a></li>
      <li>OCamlMakefile</li>
      </ul>

<?php
  if($flux = simplexml_load_file('http://'.$domain.'/export/rss20_newreleases.php?group_id='.$group_id.'&limit=1'))
  {
    $donnee = $flux->channel;

    //Lecture des données

    foreach($donnee->item as $valeur)
    {
      $version = preg_replace('/\S* (.*)$/', '$1', $valeur->title);
      $url=$valeur->link;
      echo '<div id="download-latest"><a href="'.$url.'">Download version '.$version.'</a></div>'."\n";
    }
  }
  else 
    echo 'Cannot determine latest version';
?>

      <div id="news">
        <h2>News</h2>
<?php

  if($flux = simplexml_load_file('http://forge.ocamlcore.org/export/rss20_news.php?group_id='.$group_id))
  {
    $donnee = $flux->channel;

    //Lecture des données

    foreach($donnee->item as $valeur)
    {
      $author = preg_replace('/.*\((.*)\)$/', '$1', $valeur->author);
      $content = preg_replace('/\n/', "<br/>\n", $valeur->description);
      $content = preg_replace('/(https?:\/\/[^\s]*)/', '<a href="$1">$1</a>', $content);
      echo '<h3>'.$valeur->title.'</h3>'."\n";
      echo '<p class="subtitle">by '.$author.', '.$valeur->pubDate.'</p>'."\n";
      echo '<p>'.$content.'</p>'."\n";
    }
  }
  else 
    echo 'Cannot read news feed';
?>
      </div>

<?php include "part-after-body.html"; ?>
  </body>
</html>
