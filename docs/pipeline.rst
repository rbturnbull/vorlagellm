=====================
VorlageLLM Pipeline
=====================



Input
=======
VorlageLLM takes as input a text critical apparatus in TEI XML format (https://www.tei-c.org/release/doc/tei-p5-doc/en/html/TC.html). 
All variation units are provided using <app> elements and all individual readings are given in <rdg> elements. 
A document for the text of the version in TEI format also needs to be provided. 
Both the apparatus and the text need to encapsulate the sections of text within an <ab> element with a shared identifier using the 'n' attribute. 
In the examples used below, the text of each verse of 1 Corinthians is given in <ab> elements 
with identifiers described in the XML specification for the The Institute for Textual Scholarship and Electronic Editing (e.g. 'B07K1V1') [`Houghton 2020 <https://www.degruyter.com/document/doi/10.1515/9783110591682-024/html>`_]. 
In the following discussion these sections will be called 'verses' due to the application to biblical texts but the <ab> sections can correspond to other types of unit of textual units.

.. _metadata:

Metadata
========

The siglum for the translation document is taken from the `n` attribute of the title in the header or it can be given as a command-line argument. VorlageLLM takes the publication information found about the document and adds it to the list of witnesses (<listWit>) in the header of the apparatus. The language of both the apparatus and the document are extracted from the `IETF language code <https://www.w3.org/International/articles/language-tags/>`_ in the `xml:lang` attribute for the <text> element in the body.

.. _corresponding_text:

Corresponding Text
==================

VorlageLLM determines the <ab> element in which the <app> is placed and finds the corresponding text in the <ab> element of the translated document. VorlageLLM then creates a prompt which asks the LLM to find the translated text which best corresponds to the section of text for that variation unit, given the context in the whole <ab> text of the apparatus. For example, if the <ab> corresponds to 1 Corinthians 1:1 and the first variation unit is at the words `\textgreek{Χριστοῦ Ἰησοῦ}`, it will provide the verse to the LLM with the lemma of the variation unit in \textgreek{⸂⸃} brackets (`\textgreek{Παῦλος κλητὸς ἀπόστολος ⸂Χριστοῦ Ἰησοῦ⸃ διὰ θελήματος θεοῦ καὶ Σωσθένης ὁ ἀδελφὸς}`) and it will provide the available readings (`\textgreek{Χριστοῦ Ἰησοῦ}` and `\textgreek{Ἰησοῦ Χριστοῦ}`), then the prompt will be provided the verse of the translation (for example `Paul, called to be an apostle of Jesus Christ through the will of God, and Sosthenes our brother,` and the LLM will be required to reproduce the text that corresponds to the variation unit (i.e. `Jesus Christ`). Extracting the corresponding text is useful for a number of reasons. First, the text is recorded in the TEI XML in the detail for the witness (<witDetail>) which aids in interpretability and allows for humans to see which words of the text were used by the LLM in making its later decision regarding readings. Secondly, it allows VorlageLLM to find verses with similar phrases to the text in question as discussed below.

.. _translation_technique_examples:

Translation technique examples
==============================

We could rely on the basic multi-lingual understanding of the LLM for it to choose the possible source readings of the translated text from the apparatus but this would not account for translation technique of the version in question. If we want the LLM to use information about the translation technique Without training a custom AI model then this needs to be provided through the context of the prompt. To do this VorlageLLM finds similar verses to the variation unit in question and provides parallel texts as examples of the translation technique to the prompt. In this way, VorlageLLM is similar to Retrieval-Augmented Generation (RAG) pipelines [https://arxiv.org/abs/2005.11401].

VorlageLLM then takes the corresponding text in the translation document and does a similarity search for similar verses across the whole document. It does this by using an embedding model to convert the text into a vector representation. It also does this for each verse in the document and stores this in a Chroma vector database. The most similar phrases to the corresponding text are found by using the cosine distance. A similar vector database is made of the apparatus with every permutation of each verse being embedded. Each reading in the <app> is embedded and similar verses found across the corpus. Then for all distinct similar verses, the translated text and the possible permutations of the source text are provided as examples of the translation technique most relevant to the current variation unit.

.. _selection_of_possible_readings:

Selection of possible readings
==============================

VorlageLLM then provides the verse of the text again to the LLM with the readings and the corresponding text of the variation unit in the translation language plus the translated verse in context. It also provides the list of similar verses in the source apparatus and the translated document. The LLM is then asked to select all possible readings which could have been the source of the translated text. The siglum for the translated version is added to all readings which were determined to be a possible source. It is also required to provide a one paragraph justification for the decisions that it makes, citing examples from the similar verses provided. This justification text is added to the <witDetail> for the translated version in the output apparatus. This aids in interpreting and scrutinizing the decisions that the LLM has made.

.. _output:

Output
======

A new version of the apparatus with the collated information about the new witness is then saved as a TEI XML file. This file can then be used for phylogenetic or other quantitative analysis using teiphy.

.. _ensemble:

Ensemble
========

To improve the results of VorlageLLM, it is possible to make predictions with multiple LLMs and then to combine the results with a majority vote. The software for performing this ensemble of results is provided as a command-line tool with VorlageLLM. If there is a tie in the number of outputs for a given reading, then the witness is included. VorlageLLM combines the justifications from all model outputs into a single <witDetail> element.
