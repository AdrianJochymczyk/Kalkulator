# -*- coding: utf-8 -*-
"""Teksty raportu. Lista elementów: str = akapit, list = punkty, str zaczynający się od '!' = ramka z wnioskiem.
**tekst** = pogrubienie."""

METODOLOGIA = [
    "**Zakres.** Zestawienie obejmuje firmy IT dla przedsiębiorstw działające w Polsce, ze szczególnym uwzględnieniem cyfryzacji budownictwa. "
    "Powstało w dwóch rundach: 20 spółek w pierwszej, ok. 80 w drugiej (biura projektowe, wdrożeniowcy, contech, kosztorysowanie, chmura i cyberbezpieczeństwo). "
    "Firmy pogrupowano w 9 segmentów.",
    "**Identyfikacja (KRS, NIP, REGON).** Oficjalne API KRS i przeglądarka RDF blokowały adres IP środowiska badawczego. "
    "Numery ustalono ze źródeł wtórnych: stopek i regulaminów stron firm, rejestr.io, imsig.pl (MSiG), krs-pobierz.pl, aleo.com, bizraport.pl i raportów ESPI. "
    "**Żaden numer nie został potwierdzony bezpośrednio w eKRS.** Przed użyciem formalnym należy je sprawdzić w wyszukiwarce KRS.",
    "**Dane finansowe mają dwa poziomy wiarygodności.**",
    ["**raport** – liczby odczytane z formularza RR ESPI/EBI, sprawozdania ESEF lub raportu rocznego (głównie spółki z GPW i NewConnect);",
     "**agregator*** – liczby ze sprawozdań złożonych do KRS, odczytane pośrednio z serwisów agregujących (rejestr.io, bizraport, aleo, firmy.ai, okredo i in.) lub z prasy. "
     "Nie zostały zweryfikowane z dokumentem, a status badania przez biegłego jest nieznany."],
    "**Rok obrotowy.** Ostatni pełny rok: 2025, gdy był dostępny, w przeciwnym razie 2024. Wyjątki (np. rok kończący się 31.03 lub 30.09) są zaznaczone. "
    "Nie użyto okresów częściowych. Dane są jednostkowe (spółka matka), chyba że kolumna typ raportu mówi inaczej.",
    "**Związek z budownictwem** oceniono w skali: rdzeń / oferta dedykowana / pośredni / marginalny / brak. Każda ocena ma źródło w karcie firmy.",
    "**Wskaźniki.** Marża netto = zysk netto / przychody. EBITDA obliczona jako EBIT + amortyzacja jest oznaczona.",
]

OGRANICZENIA = [
    ["**Identyfikatory nie zweryfikowane w eKRS** (blokada IP). Tam, gdzie pewność jest niższa, opisano to w uwagach przy firmie.",
     "**Większość danych finansowych pochodzi z agregatorów.** Status badania nie jest znany, etykiety lat bywają przesunięte, a serwisy czasem się różnią. Rozbieżności opisano w uwagach.",
     "**Brak plików PDF dla spółek prywatnych.** E-sprawozdania XML są dostępne tylko w RDF, który był zablokowany. Lokalne PDF-y mają tylko spółki giełdowe z pierwszej rundy.",
     "**Różne lata i definicje.** Lata obrotowe różnią się między firmami. Przychody operacyjne (MSSF) to nie to samo co przychody netto ze sprzedaży (UoR), a zysku brutto ze sprzedaży nie ma w układzie rodzajowym.",
     "**Spółki zależne grup zagranicznych** (np. biura projektowe, dostawcy BIM/CAD) raportują w Polsce tylko polską spółkę. Jej przychody nie odzwierciedlają skali grupy, a część oddziałów nie publikuje danych.",
     "**Spółki osobowe i JDG** (część producentów oprogramowania kosztorysowego) nie mają KRS ani publicznych sprawozdań, dlatego je pominięto.",
     "**Zdarzenia po dniu bilansowym**: połączenia i przejęcia (np. Shoper → cyber_Folks, Develogic → Symfonia).",
     "Załącznik wspomniany w pierwszym poleceniu nie był dostępny. Raport opiera się wyłącznie na źródłach publicznych."],
]

ANALIZA = [
    "**Skala.** Zestawienie obejmuje 98 firm w 9 segmentach. Przychody ustalono dla 71, zysk netto dla 64. Dane z raportów rocznych lub ESPI ma 20 spółek, głównie z GPW. "
    "Największe przychody jednostkowe mają:",
    ["Asseco Poland: 1,70 mld zł,",
     "Comarch: ok. 1,42 mld zł*,",
     "Elektrotim: 579 mln zł (bardziej wykonawca instalacji i automatyki budynkowej niż firma IT),",
     "Comp: 561 mln zł,",
     "Asseco BS: 478 mln zł,",
     "Wasko: 388 mln zł,",
     "Asseco Data Systems: ok. 366 mln zł*,",
     "Euvic: 360 mln zł,",
     "Text: 329 mln zł,",
     "Exatel: ok. 325 mln zł* (2024),",
     "KIR: 305 mln zł*."],
    "**Rentowność.** Najwyższą marżę netto (przy przychodach od 5 mln zł) mają:",
    ["Fakturownia: ok. 44%*, przy czym w mianowniku są przychody operacyjne,",
     "ArCADiasoft i Athenasoft: ok. 40%*,",
     "Sygnity i Text: ok. 35-36%,",
     "Sekocenbud: 35%*,",
     "Vercom: 34%."],
    "Mediana marży w segmentach:",
    ["obieg dokumentów / KSeF (15%), kosztorysowanie i inżynieria (14%) oraz SaaS B2B (12%) są najbardziej rentowne;",
     "biura projektowe (ok. 1,4%) i contech (ok. 3%) są najmniej rentowne, bo w tych segmentach przeważają usługi i polskie spółki zależne dystrybuujące licencje.",
     "Straty mają m.in. DataWalk, Synerise, Autenti, Symfonia, Develogic, Exatel oraz kilka biur projektowych: Kuryłowicz, Mott MacDonald, Ramboll i Egis."],
    "**Budownictwo: kto jest najbliżej.** Budownictwo jest głównym rynkiem 29 firm, a 8 kolejnych ma dla niego dedykowaną ofertę. Rdzeń tworzą trzy grupy:",
    ["**biura projektowe** (Sweco, Transprojekt Gdański, Multiconsult, Egis, WSP, Ramboll, Mott MacDonald, Arcadis oraz pracownie JEMS, APA Wojciechowski, Kuryłowicz i HRA). "
     "Są głównym odbiorcą narzędzi BIM. Mają duże przychody (do ok. 160 mln zł), ale niskie marże;",
     "**dostawcy BIM/CAD i contech**: Autodesk, Bentley i Trimble przez polskie spółki, ich partnerzy Graitec, Arkance i CAD Projekt K&A oraz PlanRadar i ProperGate. "
     "Polskie spółki dystrybucyjne są małe (6-20 mln zł) i w 2025 r. część z nich straciła przychody;",
     "**kosztorysowanie i oprogramowanie inżynierskie**: Athenasoft (Norma, Intercenbud), Sekocenbud, Datacomp IT (ZUZIA), Sankom (Audytor), Intersoft, Chandney (WinBud) i Koprinet (Rodos). "
     "To małe (1-20 mln zł), ale bardzo rentowne nisze."],
    "**Oferta dedykowana u dużych dostawców:**",
    ["ERP dla budownictwa: Asseco BS, Symfonia (z Develogic), IFS (IFS Cloud dla firm projektowych i budowlanych) i Hicron (SAP);",
     "inne rozwiązania branżowe: Autodesk (Construction Cloud), Sescom (facility management) i Fakturownia (oferta dla branży budowlanej)."],
    "**Integratorzy vs SaaS vs ERP.**",
    ["Największy wolumen mają integratorzy i software house'y (mediana 252 mln zł): Asseco Poland, Comp, Wasko, Euvic, Atende, Sygnity i Spyrosoft.",
     "SaaS B2B to wiele średnich firm (mediana ok. 46 mln zł) o wysokich marżach. Wyróżniają się inFakt (173 mln zł*), Text, Vercom, Shoper i Fakturownia, ale z budownictwem są związane słabo.",
     "Wdrożeniowcy ERP (Hicron, All for One, IFS, Inetum, BPX) są duzi, ale mają słabo dostępne dane publiczne. Tylko OPTeam ma dane z raportu."],
    "!**Wniosek dla segmentu budowlanego.** Cyfryzacja budownictwa w Polsce dzieli się na trzy grupy:",
    ["projektowanie, w którym BIM jest już standardem w dużych biurach;",
     "małe, rentowne narzędzia kosztorysowe;",
     "ogólne ERP z modułami branżowymi."],
    "Brakuje dużego krajowego gracza, który łączyłby kosztorys, budżet budowy, podwykonawców, rozliczanie robót, dokumentację z placu budowy i flotę w jednym SaaS. "
    "Najbliżej są Symfonia z Develogic, ABS i IFS. Contech (PlanRadar, ProperGate) jest w Polsce dopiero na etapie kilku milionów złotych przychodów. "
    "Firma, która połączy dane z kosztorysów (Norma, ZUZIA, Rodos) z zarządzaniem realizacją, ma wolną przestrzeń rynkową.",
]
