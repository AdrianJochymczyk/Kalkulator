# -*- coding: utf-8 -*-
"""Buduje CSV i wykresy dla raportu o polskich spółkach IT (stan na 2026-11-20).

Dane finansowe w tys. PLN. Pole `zrodlo_fin`:
  "pierwotne"  - odczytane bezpośrednio z raportu rocznego / ESPI / ESEF
  "agregator"  - dane ze sprawozdań złożonych w KRS, odczytane pośrednio z serwisów
                 (rejestr.io, bizraport.pl, aleo.com, firmy.ai itp.) przez wyniki wyszukiwania;
                 wymagają potwierdzenia w RDF (ekrs.ms.gov.pl)
Uruchomienie: python3 research/build.py
"""
import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
NIE = "nie ustalono"


def rj(krs):
    return f"https://rejestr.io/krs/{int(krs)}"


M = "https://money2.wpcdn.pl/gielda/gpw/raporty/2026/03/"

COMPANIES = [
    # ---------------- spółki giełdowe / dane pierwotne ----------------
    dict(
        nazwa="Asseco Poland S.A.", krs="0000033391", nip="5220003782", regon="010334578",
        siedziba="ul. Olchowa 14, 35-322 Rzeszów", www="https://pl.asseco.com",
        kategoria="Integrator IT / producent oprogramowania (GPW: ACP)",
        produkt="Własne systemy dla bankowości, ubezpieczeń, administracji, zdrowia, energetyki; wdrożenia ERP (m.in. Microsoft Dynamics)",
        opis="Największy polski producent oprogramowania i spółka matka międzynarodowej Grupy Asseco. Projektuje, wdraża i utrzymuje systemy dla finansów, sektora publicznego (m.in. ZUS), ochrony zdrowia, utilities i przedsiębiorstw.",
        budownictwo="Pośredni: case study wdrożenia Microsoft Dynamics AX z modyfikacjami branżowymi (rejestr umów, kaucje gwarancyjne inwestor/podwykonawca) w Eiffage Budownictwo Mitex S.A. (https://pl.asseco.com/en/case-study/eiffage-budownictwo-mitex-sa-microsoft-dynamix-ax-60)",
        poziom_bud="pośredni",
        rok="2025", przychody=1703400, zysk_brutto_sprz=551200, ebit=342600, zysk_netto=432700, ebitda=414300,
        ebitda_uwagi="EBITDA obliczona: EBIT 342,6 + amortyzacja 71,7 mln zł (rachunek przepływów); nie jest wielkością raportowaną jednostkowo",
        waluta="PLN", typ="jednostkowe (MSSF), badane", data_pub="2026-03-31", zrodlo_fin="pierwotne",
        link_raportu=M + "20260331_191944_0510033759_YE25_Sprawozdanie_jednostkowe_Asseco_Poland.xhtml",
        plik="reports/Asseco_Poland_2025_jednostkowe_sprawozdanie_finansowe.pdf",
        uwagi="Przychody = 'przychody operacyjne' MSSF. Zysk netto zawiera wysokie przychody finansowe (dywidendy od spółek zależnych) - dlatego zysk netto > EBIT. Skonsolidowane 2025: przychody 16 779,8 mln zł, zysk netto przypisany akcjonariuszom 1 138,7 mln zł (z zyskiem ok. 499 mln zł ze sprzedaży akcji Sapiens). ESPI RR: https://www.money.pl/gielda/raporty/raport,plsoftb00016,7271046741824577.html",
    ),
    dict(
        nazwa="Comarch S.A.", krs="0000057567", nip="6770065406", regon="350527377",
        siedziba="al. Jana Pawła II 39A, 31-864 Kraków", www="https://www.comarch.pl",
        kategoria="Producent ERP/SaaS + integrator IT (od 26.03.2025 poza GPW)",
        produkt="Comarch ERP XL / Optima / Altum, CRM i lojalność, OSS/BSS, systemy dla finansów i zdrowia, chmura/data center",
        opis="Polski producent oprogramowania i integrator. Linie ERP dla MŚP i dużych firm (XL, Optima, Altum, w tym w chmurze), systemy dla telekomów, bankowości, ubezpieczeń, handlu, sektora publicznego i zdrowia; własne centra danych.",
        budownictwo="Pośredni: case studies Comarch ERP XL/CDN XL w firmach budowlanych ALSTAL Grupa Budowlana (https://www.comarch.pl/files-pl/file_111/ALSTALGB-CS.pdf) i ELMO SA (https://www.comarch.pl/files-pl/file_115/ELMO-SA.pdf); brak dedykowanego modułu budowlanego",
        poziom_bud="pośredni",
        rok="2025", przychody=1417910, zysk_brutto_sprz=None, ebit=None, zysk_netto=120493, ebitda=None,
        ebitda_uwagi="EBITDA Grupy 2025: 381 mln zł (raport roczny, s. 24)",
        waluta="PLN", typ="jednostkowe (agregator, dane z KRS); grupa: skonsolidowane z raportu rocznego", data_pub="2026-04 (raport roczny)", zrodlo_fin="agregator",
        link_raportu="https://www.comarch.pl/files-pl/file_1234/Comarch-Raport-Roczny-2025.pdf",
        plik="reports/Comarch_2025_raport_roczny.pdf",
        uwagi="Raport roczny 2025 (PDF) podaje tylko dane Grupy: przychody 1 714 mln zł (+6% r/r), EBITDA 381 mln zł, zakontraktowanie 1 935 mln zł - zweryfikowane w PDF. Dane jednostkowe 2025 (przychody netto 1 417 910 tys., zysk netto 120 493 tys.) pochodzą z bizraport.pl (sprawozdanie z KRS) i nie zostały zweryfikowane w dokumencie źródłowym. Kontrolnie: jednostkowe 2024 wg QSr 4/2024: przychody 1 341 703 tys., zysk netto 112 402 tys. (https://www.comarch.pl/files-pl/file_793/QSr_4_2024.pdf).",
    ),
    dict(
        nazwa="Asseco Business Solutions S.A.", krs="0000028257", nip="5222612717", regon="017293003",
        siedziba="ul. Konrada Wallenroda 4C, 20-607 Lublin", www="https://assecobs.pl",
        kategoria="Dostawca ERP / producent SaaS (GPW: ABS)",
        produkt="Macrologic ERP, Softlab ERP, WAPRO ERP (KSeF), Asseco HR, Mobile Touch (SFA), e-commerce B2B",
        opis="Producent własnych systemów ERP dla MŚP i dużych firm (on-premise i chmura), systemów HR, mobilnych systemów sprzedaży i platform B2B; klienci z produkcji, dystrybucji, FMCG, usług i biur rachunkowych.",
        budownictwo="Bezpośredni (oferta branżowa): strona 'ERP dla budownictwa' - budżety i harmonogramy projektów, kosztorysy, rezerwacja sprzętu, rozliczanie per projekt/budowa, faktury powiązane z protokołami odbioru (https://assecobs.pl/erp/construction/?lang=en)",
        poziom_bud="oferta dedykowana",
        rok="2025", przychody=478358, zysk_brutto_sprz=212308, ebit=145803, zysk_netto=133689, ebitda=186377,
        ebitda_uwagi="EBITDA obliczona: EBIT 145 803 + amortyzacja 40 574 tys. zł",
        waluta="PLN", typ="jednostkowe (MSSF), badane", data_pub="2026-03-04", zrodlo_fin="pierwotne",
        link_raportu="https://assecobs.pl/wp-content/uploads/2025/04/Jednostkowe_Sprawozdanie_finansowe_ABS_2025.xhtml",
        plik="reports/Asseco_Business_Solutions_2025_jednostkowe_sprawozdanie_finansowe.pdf",
        uwagi="Wybrane dane: https://assecobs.pl/wp-content/uploads/2025/04/2025_Wybrane_dane_finansowe_Asseco_Business_Solutions.xhtml. Skonsolidowane 2025: przychody ok. 476,8 mln zł, zysk netto ok. 132,7-132,9 mln zł (prezentacja wyników).",
    ),
    dict(
        nazwa="Sygnity S.A.", krs="0000008162", nip="5860005293", regon="190407926",
        siedziba="ul. Postępu 17B, 02-676 Warszawa", www="https://www.sygnity.pl",
        kategoria="Integrator IT / konsultant IT (GPW: SGN)",
        produkt="Systemy dedykowane i własne dla administracji publicznej, finansów, energetyki; utrzymanie i outsourcing",
        opis="Integrator i producent oprogramowania, głównie dla administracji centralnej i samorządowej, bankowości, ubezpieczeń, energetyki i przedsiębiorstw; budowa systemów dedykowanych, utrzymanie, outsourcing.",
        budownictwo="Brak potwierdzonego związku",
        poziom_bud="brak",
        rok="2025", przychody=252459, zysk_brutto_sprz=118336, ebit=87099, zysk_netto=90690, ebitda=92351,
        ebitda_uwagi="EBITDA obliczona: EBIT 87 099 + amortyzacja 5 252 tys. zł",
        waluta="PLN", typ="jednostkowe (MSSF), badane", data_pub="2026-03-24", zrodlo_fin="pierwotne",
        link_raportu=M + "20260324_204010_1904899437_JSF-Sygnity-2025-12-31-1-pl.xhtml",
        plik="reports/Sygnity_2025_jednostkowe_sprawozdanie_finansowe.pdf",
        uwagi="ESPI RR: https://www.money.pl/gielda/raporty/raport,plcmpld00016,7268229468722241.html. Skonsolidowane 2025: przychody 350 256 tys., EBIT 89 482 tys., zysk netto 77 260 tys. (wg komunikatów; nie weryfikowano w SSF).",
    ),
    dict(
        nazwa="Vercom S.A.", krs="0000535618", nip="7811765125", regon="300061423",
        siedziba="ul. Wierzbięcice 1B, 61-569 Poznań", www="https://vercom.pl",
        kategoria="Producent SaaS / CPaaS (GPW: VRC)",
        produkt="Platformy komunikacji API: SMSAPI, EmailLabs, Mailjet (e-mail i SMS transakcyjne/marketingowe)",
        opis="Dostawca platform CPaaS do automatyzacji komunikacji e-mail/SMS z klientami; obsługuje e-commerce, handel, finanse i firmy technologiczne w Polsce i za granicą.",
        budownictwo="Brak potwierdzonego związku",
        poziom_bud="brak",
        rok="2025", przychody=240864, zysk_brutto_sprz=None, ebit=72834, zysk_netto=80885, ebitda=80810,
        ebitda_uwagi="EBITDA obliczona: EBIT 72 834 + amortyzacja 7 976 tys. zł; rachunek w układzie rodzajowym (brak zysku brutto ze sprzedaży)",
        waluta="PLN", typ="jednostkowe (MSSF), badane", data_pub="2026-03-18", zrodlo_fin="pierwotne",
        link_raportu=M + "20260318_065948_1206312055_JSF_vrc-2025-12-31-1-pl.xhtml",
        plik="reports/Vercom_2025_jednostkowe_sprawozdanie_finansowe.pdf",
        uwagi="Spadek przychodów jednostkowych r/r (288 004 -> 240 864 tys.). Skonsolidowane 2025: przychody 471 152 tys., zysk netto akcjonariuszy 89 866 tys. ESPI RR: https://www.money.pl/gielda/raporty/raport,plvrcm000016,7266106906333761.html",
    ),
    dict(
        nazwa="Shoper S.A. (od 01.09.2026 przejęta przez cyber_Folks S.A.)", krs="0000395171", nip="9452156998", regon="121495203",
        siedziba="ul. Pawia 9, 31-154 Kraków (do połączenia)", www="https://www.shoper.pl",
        kategoria="Producent SaaS (e-commerce)",
        produkt="Platforma SaaS do sklepów internetowych (abonament) z płatnościami, logistyką i marketingiem",
        opis="Polska platforma SaaS e-commerce dla MŚP; segment Subscriptions i Solutions (płatności, wysyłki, marketing).",
        budownictwo="Marginalny: poradnik sprzedaży artykułów budowlanych online, klienci-sklepy z wyrobami dla budownictwa (np. e-armet.pl); brak modułu branżowego",
        poziom_bud="marginalny",
        rok="2025", przychody=193467, zysk_brutto_sprz=None, ebit=45187, zysk_netto=35409, ebitda=61366,
        ebitda_uwagi="EBITDA raportowana w formularzu RR (skorygowana EBITDA 65 821 tys.)",
        waluta="PLN", typ="jednostkowe (MSSF), badane", data_pub="2026-03-18", zrodlo_fin="pierwotne",
        link_raportu=M + "20260318_070317_0996477630_JSF-Shoper-2025-12-31.xhtml",
        plik="reports/Shoper_2025_jednostkowe_sprawozdanie_finansowe.pdf",
        uwagi="Połączenie z cyber_Folks S.A. (KRS 0000685595) zarejestrowane 01.09.2026 - Shoper S.A. jako podmiot przejmowany przestaje istnieć; FY2025 to ostatni pełny rok samodzielny. Skonsolidowane 2025: przychody 217 974 tys., zysk netto 43 083 tys. ESPI RR: https://www.money.pl/gielda/raporty/raport,plshpr000021,7266106714673729.html",
    ),
    dict(
        nazwa="Text S.A. (dawniej LiveChat Software S.A.)", krs="0000290756", nip="8992447196", regon="932803200",
        siedziba="ul. Zwycięska 47, 53-033 Wrocław", www="https://www.text.com",
        kategoria="Producent SaaS (GPW: TXT)",
        produkt="LiveChat, ChatBot, HelpDesk, KnowledgeBase, OpenWidget - SaaS do obsługi klienta i sprzedaży z AI",
        opis="Producent globalnych aplikacji SaaS do komunikacji z klientem; sprzedaż głównie za granicą (USD), klienci z wielu branż.",
        budownictwo="Marginalny: strona marketingowa 'LiveChat for construction companies' (https://www.livechat.com/solutions/construction-companies/); brak potwierdzonych wdrożeń",
        poziom_bud="marginalny",
        rok="2025/26 (01.04.2025-31.03.2026)", przychody=329073, zysk_brutto_sprz=222320, ebit=126258, zysk_netto=115935, ebitda=152654,
        ebitda_uwagi="EBITDA raportowana (wybrane jednostkowe dane finansowe)",
        waluta="PLN", typ="jednostkowe (MSR od 01.04.2024), badane", data_pub="2026-06-26", zrodlo_fin="pierwotne",
        link_raportu="https://investor.text.com/uploads/txt_spraw_zarzadu-2026-03-31-1-pl.xhtml",
        plik="reports/Text_2025-26_sprawozdanie_zarzadu.pdf",
        uwagi="Rok obrotowy kończy się 31 marca - nieporównywalny 1:1 z rokiem kalendarzowym. Skonsolidowane 2025/26: zysk netto 116,6 mln zł, EBITDA 153,3 mln zł.",
    ),
    dict(
        nazwa="iFirma S.A.", krs="0000281947", nip="8981647572", regon="931082394",
        siedziba="ul. Grabiszyńska 241G, 53-234 Wrocław", www="https://www.ifirma.pl",
        kategoria="Producent SaaS (księgowość, fakturowanie, KSeF) + biuro rachunkowe online (GPW: IFI)",
        produkt="ifirma.pl - księgowość i fakturowanie online z integracją KSeF; usługi biura rachunkowego",
        opis="Internetowa księgowość i fakturowanie w modelu SaaS dla JDG i małych spółek, z bezpłatną integracją z KSeF (wysyłka faktur sprzedaży, import zakupowych) i usługami biura rachunkowego.",
        budownictwo="Brak dedykowanego modułu (obsługa KSeF ogólnobranżowa)",
        poziom_bud="brak",
        rok="2025", przychody=63390, zysk_brutto_sprz=None, ebit=15455, zysk_netto=13017, ebitda=15926,
        ebitda_uwagi="EBITDA obliczona: EBIT 15 455 + amortyzacja 471 tys. zł; sprawozdanie wg UoR (brak pozycji zysk brutto ze sprzedaży w układzie MSSF)",
        waluta="PLN", typ="jednostkowe (UoR), badane (4Audyt)", data_pub="2026-03-20", zrodlo_fin="pierwotne",
        link_raportu="https://www.ifirma.pl/wp-content/raporty-xml/SAR-2025/raportroczny-SAR_08RoczneSF2025.xhtml",
        plik="reports/iFirma_2025_sprawozdanie_finansowe.pdf",
        uwagi="Spółka publikuje wyłącznie raport jednostkowy. ESPI RR: https://www.money.pl/gielda/raporty/raport,plpwrmd00011,7266460758348353.html",
    ),
    # ---------------- spółki prywatne / dane z agregatorów ----------------
    dict(
        nazwa="Symfonia sp. z o.o.", krs="0000228956", nip="5262831503", regon="140045209",
        siedziba="Al. Jerozolimskie 132, 02-305 Warszawa", www="https://symfonia.pl",
        kategoria="Dostawca ERP / HR / SaaS (dawniej Sage Symfonia; właściciel: Accel-KKR)",
        produkt="Symfonia ERP (FK, kadry-płace, handel, produkcja), rozwiązania chmurowe; od 12.2025 Develogic ERP dla budownictwa",
        opis="Producent oprogramowania ERP, HR i księgowego dla MŚP i średnich firm; rośnie przez akwizycje (Polska, Rumunia, Austria); wdrożenia własne i przez partnerów.",
        budownictwo="Silny: przejęcie Develogic (ERP dla deweloperów i GW) w grudniu 2025 (https://symfonia.pl/blog/aktualnosci-symfonii/develogic-dolacza-do-grupy-symfonia-nowy-etap-na-drodze-do-cyfryzacji-branzy-budowlanej/), strona 'ERP dla firm budowlanych' (https://symfonia.pl/erp/erp-dla-firm-budowlanych/), referencje Karmar, Marvipol",
        poziom_bud="oferta dedykowana",
        rok="01.10.2024-30.09.2025", przychody=227960, zysk_brutto_sprz=None, ebit=None, zysk_netto=-55537, ebitda=29640,
        ebitda_uwagi="EBITDA wg firmy.ai (niezweryfikowana)",
        waluta="PLN", typ="jednostkowe (agregator: firmy.ai/rejestr.io), status badania nie ustalono", data_pub=NIE, zrodlo_fin="agregator",
        link_raportu="https://rejestr.io/krs/228956/symfonia/sprawozdania",
        plik="",
        uwagi="Rok obrotowy do 30 września. Rozbieżność: strata -55,5 mln zł (jednostkowa wg firmy.ai/rejestr.io) vs -37,5 mln zł (skonsolidowana wg bizraport.pl). Grupa Symfonia: ok. 250 mln zł przychodu za rok do 30.09.2024 (https://itwiz.pl/grupa-symfonia-z-blisko-250-mln-zl-przychodu-za-2024-rok/). Źródła: https://firmy.ai/KRS/0000228956, https://www.bizraport.pl/krs/0000228956/symfonia-spolka-z-ograniczona-odpowiedzialnoscia",
    ),
    dict(
        nazwa="IT.integro sp. z o.o.", krs="0000014040", nip="7780021279", regon="632507882",
        siedziba="ul. Ząbkowicka 12, 60-166 Poznań (wg KRS; część serwisów podaje adres w Warszawie)", www="https://itintegro.com",
        kategoria="Integrator / wdrożeniowiec ERP (partner Microsoft Dynamics 365) + ISV",
        produkt="Wdrożenia Microsoft Dynamics 365 Business Central; ponad 30 aplikacji na Microsoft AppSource",
        opis="Partner Microsoft Dynamics od 1991 r.; wdraża Business Central w Polsce i ponad 60 krajach; obsługuje usługi profesjonalne, handel/dystrybucję, produkcję i logistykę.",
        budownictwo="Brak potwierdzonego związku",
        poziom_bud="brak",
        rok="2025", przychody=128935, zysk_brutto_sprz=None, ebit=15400, zysk_netto=14479, ebitda=None, ebitda_uwagi="",
        waluta="PLN", typ="jednostkowe (agregator: bizraport/aleo), status badania nie ustalono", data_pub=NIE, zrodlo_fin="agregator",
        link_raportu="https://rejestr.io/krs/14040/it-integro",
        plik="",
        uwagi="Przychody = przychody netto ze sprzedaży produktów ok. 128,9 mln zł (razem ok. 132,9 mln zł); EBIT ok. 15,4 mln zł. Źródła: https://www.bizraport.pl/krs/0000014040/it-integro-spolka-z-ograniczona-odpowiedzialnoscia, https://aleo.com/int/company/it.-integro-spolka-z-ograniczona-odpowiedzialnoscia",
    ),
    dict(
        nazwa="InsERT S.A.", krs="0000306888", nip="8981945134", regon="932283479",
        siedziba="ul. Jerzmanowska 2, 54-519 Wrocław", www="https://www.insert.com.pl",
        kategoria="Dostawca ERP / oprogramowania księgowego dla MŚP",
        produkt="Subiekt, Rachmistrz, Rewizor, Gratyfikant (linie GT i nexo), integracja z KSeF",
        opis="Producent masowego oprogramowania dla mikro i małych firm oraz biur rachunkowych (sprzedaż/magazyn, księgowość, kadry-płace); dystrybucja przez sieć partnerów.",
        budownictwo="Brak dedykowanego modułu (jedynie rekomendacje partnerów dla małych firm remontowych)",
        poziom_bud="brak",
        rok="2025", przychody=103887, zysk_brutto_sprz=None, ebit=4460, zysk_netto=4174, ebitda=None, ebitda_uwagi="",
        waluta="PLN", typ="jednostkowe (agregator: bizraport/rejestr.io), status badania nie ustalono", data_pub=NIE, zrodlo_fin="agregator",
        link_raportu="https://rejestr.io/krs/306888/insert/sprawozdania",
        plik="",
        uwagi="Przychody = przychody operacyjne ok. 103,9 mln zł (przychody ogółem 104,2 mln zł); pozycja 'przychody netto ze sprzedaży' nie została wyodrębniona. 2024: przychody ok. 91,3-91,6 mln zł, zysk netto 4,3 mln zł. Źródło: https://www.bizraport.pl/krs/0000306888/insert-spolka-akcyjna",
    ),
    dict(
        nazwa="Forterro Polska sp. z o.o. (dawniej BPSC)", krs="0000705385", nip="6340134346", regon="003469134",
        siedziba="Al. Walentego Roździeńskiego 188H, 40-203 Katowice", www="https://www.bpsc.com.pl",
        kategoria="Dostawca i wdrożeniowiec ERP/MES (Grupa Forterro)",
        produkt="BPSC ERP (dawniej Impuls EVO): finanse, HR, produkcja/MES, sprzedaż, logistyka, CRM, zarządzanie projektami",
        opis="Producent i wdrożeniowiec własnego systemu ERP, głównie dla przemysłu (m.in. Famur, Tauron, GH Cranes); od 2025 r. pod nazwą Forterro Polska.",
        budownictwo="Brak potwierdzonego związku (referencje z przemysłu)",
        poziom_bud="brak",
        rok="2025 (prawdopodobnie - wg etykiety rejestr.io)", przychody=93963, zysk_brutto_sprz=None, ebit=28371, zysk_netto=24058, ebitda=None, ebitda_uwagi="",
        waluta="PLN", typ="jednostkowe (agregator: rejestr.io/bizraport), status badania nie ustalono", data_pub=NIE, zrodlo_fin="agregator",
        link_raportu="https://rejestr.io/krs/705385/forterro-polska",
        plik="",
        uwagi="Przychody netto ze sprzedaży 93 963 tys. (przychody ogółem 96 859 tys.). Rok przypisany na podstawie rejestr.io ('dane za 2025'); bizraport nie podaje roku. Źródło: https://www.bizraport.pl/krs/0000705385/forterro-polska-spolka-z-ograniczona-odpowiedzialnoscia; zmiana nazwy: https://www.bpsc.com.pl/pl/aktualnosci/forterro-polska-zamiast-bpsc",
    ),
    dict(
        nazwa="Streamsoft sp. z o.o. sp.k.", krs="0000443818", nip="9291851723", regon="081108705",
        siedziba="Al. Wojska Polskiego 11, 65-077 Zielona Góra", www="https://streamsoft.pl",
        kategoria="Dostawca i wdrożeniowiec ERP (MŚP i średnie firmy)",
        produkt="Streamsoft Verto, Streamsoft Prestiż (finanse, kadry-płace, handel, logistyka, produkcja, BI)",
        opis="Producent ERP z ponad 5000 klientów; wdrożenia bezpośrednie i przez partnerów, m.in. dystrybucja stali (Centrostal), stolarka okienna (Plastixal).",
        budownictwo="Pośredni/marginalny: klienci z branży materiałów budowlanych (Centrostal, Plastixal), brak klientów-wykonawców",
        poziom_bud="marginalny",
        rok="2025", przychody=84700, zysk_brutto_sprz=None, ebit=6530, zysk_netto=5304, ebitda=None, ebitda_uwagi="",
        waluta="PLN", typ="jednostkowe (agregator: bizraport/aleo), status badania nie ustalono", data_pub=NIE, zrodlo_fin="agregator",
        link_raportu="https://rejestr.io/krs/443818",
        plik="",
        uwagi="Rozbieżność: analizafirm.pl podaje przychody netto 92 410 tys. i zysk netto ok. 6 780 tys. Komplementariusz: Streamsoft sp. z o.o. (KRS 0000434736). Źródła: https://www.bizraport.pl/krs/0000443818/streamsoft-spolka-z-ograniczona-odpowiedzialnoscia-spolka-komandytowa, https://analizafirm.pl/firma/0000443818/streamsoft",
    ),
    dict(
        nazwa="Soneta sp. z o.o. (enova365)", krs="0000109244", nip="6792705304", regon="356381673",
        siedziba="ul. J. Kustronia 44A, 30-432 Kraków", www="https://www.enova.pl",
        kategoria="Dostawca ERP / HR (kanał partnerski)",
        produkt="enova365 (FK, kadry-płace, handel/magazyn, CRM, workflow, BI), TRIVA",
        opis="Producent systemu ERP enova365 sprzedawanego przez sieć partnerów wdrożeniowych firmom MŚP i większym w wielu branżach.",
        budownictwo="Pośredni (przez partnerów): system zarządzania budową na enova365 dla BPBP S.A. (https://www.enova.pl/content/uploads/2025/09/enova365-bpbp-s.a.-case-study-mg-rozszerzone.pdf), wdrożenie PEUiM (https://www.enova.pl/content/uploads/2026/01/peuim.pdf), Corleonis (wynajem żurawi)",
        poziom_bud="pośredni",
        rok="2025", przychody=76583, zysk_brutto_sprz=None, ebit=None, zysk_netto=None, ebitda=None, ebitda_uwagi="",
        waluta="PLN", typ="jednostkowe (agregator: sprawozdaniaonline.pl), status badania nie ustalono", data_pub=NIE, zrodlo_fin="agregator",
        link_raportu="https://sprawozdaniaonline.pl/SprawozdaniaFinansowe/0000109244/SONETA-SPOLKA-Z-OGRANICZONA-ODPOWIEDZIALNOSCIA",
        plik="",
        uwagi="Zysk netto 2025 nie ustalono (EMIS podaje jedynie dynamikę +106% r/r). 2023: przychody ok. 61,7 mln zł, zysk netto 8 051 tys. zł (gowork.pl). Spółka z grupy Asseco.",
    ),
    dict(
        nazwa="Athenasoft sp. z o.o. (Norma, Intercenbud)", krs="0000035122", nip="1131896687", regon="012924870",
        siedziba="ul. Leszczynowa 7, 03-197 Warszawa", www="https://ath.pl",
        kategoria="Dostawca rozwiązania budowlanego (kosztorysowanie + cenniki)",
        produkt="Norma EXPERT, Norma STANDARD 2, Norma PRO; baza cen INTERCENBUD",
        opis="Producent wiodącego w Polsce oprogramowania kosztorysowego Norma oraz operator bazy cenowej INTERCENBUD; użytkownicy: kosztorysanci, projektanci, wykonawcy, inwestorzy, inspektorzy nadzoru, rzeczoznawcy.",
        budownictwo="Rdzeń działalności: kosztorysowanie i cenniki budowlane (https://ath.pl/pl-pl/produkty/baza-cen-intercenbud, https://blog.intercenbud.pl/kontakt/)",
        poziom_bud="rdzeń",
        rok="2025", przychody=20212, zysk_brutto_sprz=None, ebit=None, zysk_netto=8051, ebitda=None, ebitda_uwagi="",
        waluta="PLN", typ="jednostkowe (agregator: bizraport/rejestr.io), status badania nie ustalono", data_pub=NIE, zrodlo_fin="agregator",
        link_raportu="https://rejestr.io/krs/35122/athenasoft",
        plik="",
        uwagi="Przychody netto ze sprzedaży 20 211,9 tys. (bizraport); rejestr.io ok. 20 980 tys. (prawdopodobnie przychody ogółem). Zysk netto 8 051,1 tys. - zgodny w dwóch serwisach. Etykieta roku 2025 niezweryfikowana datą złożenia. Intercenbud to marka Athenasoft, nie odrębna spółka.",
    ),
    dict(
        nazwa="SEKOCENBUD sp. z o.o.", krs="0000092639", nip="5260210441", regon="001266562",
        siedziba="ul. Puławska 182, 02-670 Warszawa", www="https://sekocenbud.pl",
        kategoria="Dostawca rozwiązania budowlanego (cenniki + kosztorysowanie)",
        produkt="System cen SEKOCENBUD (biuletyny, SEKOCENBUD NET), program kosztorysowy SeKo",
        opis="Wydawca systemu informacji cenowej SEKOCENBUD (biuletyny drukowane i elektroniczne, portal cenowy) oraz programu kosztorysowego SeKo; do 30.06.2023 jako OWEOB 'Promocja' sp. z o.o.",
        budownictwo="Rdzeń działalności: ceny i kosztorysowanie robót budowlanych, wykorzystywane m.in. przez inwestorów publicznych (https://sekocenbud.pl/o-firmie/)",
        poziom_bud="rdzeń",
        rok="2025", przychody=11925, zysk_brutto_sprz=None, ebit=None, zysk_netto=4132, ebitda=None, ebitda_uwagi="",
        waluta="PLN", typ="jednostkowe (agregator: rejestr.io), status badania nie ustalono", data_pub=NIE, zrodlo_fin="agregator",
        link_raportu="https://rejestr.io/krs/92639/sekocenbud",
        plik="",
        uwagi="2024: przychody ok. 11,2 mln zł, zysk ok. 3,9 mln zł (aleo); 2023: 10 501 / 3 826 tys. (bizraport).",
    ),
    dict(
        nazwa="Develogic sp. z o.o.", krs="0000873823", nip="8971731779", regon="020562490",
        siedziba="Poznań (adres ulicy nie potwierdzony w KRS)", www="https://develogic.pl",
        kategoria="Dostawca ERP dla budownictwa i deweloperów (od 12.2025 w Grupie Symfonia)",
        produkt="Develogic ERP: budżetowanie inwestycji, zakupy i umowy z podwykonawcami, zarządzanie budową, CRM i sprzedaż lokali, finanse",
        opis="ERP dla deweloperów, generalnych wykonawców, podwykonawców i inwestorów; sprzedawany wspólnie jako 'Symfonia + Develogic'.",
        budownictwo="Rdzeń działalności: ERP dla deweloperów i GW (https://symfonia.pl/oprogramowanie/branza-budowlana/)",
        poziom_bud="rdzeń",
        rok="2025", przychody=8600, zysk_brutto_sprz=None, ebit=None, zysk_netto=-1375, ebitda=None, ebitda_uwagi="",
        waluta="PLN", typ="jednostkowe (agregator: rejestr.io/nipregon), status badania nie ustalono", data_pub=NIE, zrodlo_fin="agregator",
        link_raportu="https://rejestr.io/krs/873823/develogic",
        plik="",
        uwagi="Przychody ok. 8,6 mln zł (zaokrąglone przez rejestr.io). 2024: przychody 7 886,6 tys., zysk netto 59,5 tys. (nipregon.pl). Średnia pewność przypisania marki do tego KRS (inny serwis podaje KRS 0000979250 - niezweryfikowane).",
    ),
    dict(
        nazwa="Datacomp IT sp. z o.o. (ZUZIA)", krs="0000936569", nip="6793228148", regon=NIE,
        siedziba="Kraków (adres siedziby w KRS nie potwierdzony)", www="https://datacomp.com.pl",
        kategoria="Dostawca rozwiązania budowlanego (kosztorysowanie, BIM 5D)",
        produkt="ZUZIA (kosztorysowanie robót budowlanych, instalacyjnych, drogowych, telekom.), ZUZIAbim",
        opis="Producent i sprzedawca pakietu kosztorysowego ZUZIA i ZUZIAbim (BIM + kosztorys) w modelu subskrypcji; klienci: kosztorysanci, wykonawcy, biura projektowe.",
        budownictwo="Rdzeń działalności: kosztorysowanie i BIM 5D (https://sklep.datacomp.com.pl/regulamin-sklepu-internetowego-datacomp/)",
        poziom_bud="rdzeń",
        rok="2024", przychody=7232, zysk_brutto_sprz=None, ebit=None, zysk_netto=-3, ebitda=None, ebitda_uwagi="",
        waluta="PLN", typ="jednostkowe (agregator: okredo/gowork), status badania nie ustalono", data_pub=NIE, zrodlo_fin="agregator",
        link_raportu="https://rejestr.io/krs/936569/datacomp-it",
        plik="",
        uwagi="REGON nie ustalono; NIP z regulaminu sklepu (niepodwójnie sprawdzony). Bizraport podaje (bez roku, możliwie 2025): przychody 8 162,5 tys., strata 166,7 tys. Pierwotny producent DATACOMP sp. z o.o. (KRS 0000193067) w likwidacji.",
    ),
    dict(
        nazwa="ArCADiasoft Chudzik sp. j.", krs="0000316955", nip="7251676810", regon="471726120",
        siedziba="ul. Sienkiewicza 85/87, 90-057 Łódź", www="https://www.arcadiasoft.pl",
        kategoria="Dostawca rozwiązania budowlanego (BIM / projektowanie konstrukcji)",
        produkt="ArCADia BIM (architektura, instalacje, konstrukcje), ArCADia-RAMA, INTERsoft",
        opis="Polski producent oprogramowania BIM/CAD dla architektów, projektantów instalacji i konstruktorów; użytkownicy to głównie biura projektowe.",
        budownictwo="Rdzeń działalności: BIM i projektowanie budowlane (https://trade.gov.pl/en/?p=56696)",
        poziom_bud="rdzeń",
        rok="2024", przychody=6354, zysk_brutto_sprz=None, ebit=None, zysk_netto=2554, ebitda=None, ebitda_uwagi="",
        waluta="PLN", typ="jednostkowe (agregator: bizraport), status badania nie ustalono", data_pub="2025-07-01 (złożenie do KRS wg bizraport)", zrodlo_fin="agregator",
        link_raportu="https://rejestr.io/krs/316955/arcadiasoft-chudzik",
        plik="",
        uwagi="Spółka jawna (wpisana do rejestru przedsiębiorców KRS). Przychody = przychody operacyjne. Aleo podaje inne etykiety lat (prawdopodobnie przesunięte). Powiązana INTERSOFT sp. z o.o. (KRS 0000126422).",
    ),
    dict(
        nazwa="ORGBUD-SERWIS sp. z o.o.", krs="0000153986", nip="7780045280", regon="004866423",
        siedziba="ul. Stablewskiego 43, Poznań", www="https://orgbud.pl",
        kategoria="Dostawca rozwiązania budowlanego (cenniki, szkolenia, dystrybucja programów kosztorysowych)",
        produkt="Informatory cenowe dla budownictwa, kursy kosztorysowania, dystrybucja programu KOBRA, księgarnia techniczna",
        opis="Poznański wydawca informacji cenowych dla budownictwa, organizator szkoleń kosztorysowych i dystrybutor oprogramowania kosztorysowego.",
        budownictwo="Rdzeń działalności: cenniki i kosztorysowanie (https://orgbud.pl/kontakt/)",
        poziom_bud="rdzeń",
        rok="2024", przychody=1511, zysk_brutto_sprz=None, ebit=None, zysk_netto=340, ebitda=None, ebitda_uwagi="",
        waluta="PLN", typ="jednostkowe (agregator: rejestr.io), status badania nie ustalono", data_pub=NIE, zrodlo_fin="agregator",
        link_raportu="https://rejestr.io/krs/153986/orgbud-serwis",
        plik="",
        uwagi="Mała spółka; bizraport podaje 1 447,0 / 273,9 tys. bez wskazania roku. Firma głównie odsprzedaje, a nie rozwija oprogramowanie.",
    ),
]

COLS = ["nazwa_spolki", "krs", "nip", "regon", "siedziba", "strona_www", "kategoria", "opis_dzialalnosci",
        "zwiazek_z_budownictwem", "rok_finansowy", "przychody", "zysk_netto", "marza_netto", "waluta",
        "typ_raportu", "link_krs", "link_raportu", "uzupelniajace_uwagi"]


def fmt(v):
    return NIE if v is None else f"{v}"


def margin(c):
    if c["przychody"] and c["zysk_netto"] is not None:
        return c["zysk_netto"] / c["przychody"] * 100
    return None


def write_csv():
    path = os.path.join(HERE, "spolki_it_polska_dane_finansowe.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for c in COMPANIES:
            m = margin(c)
            extra = [
                f"jednostki: tys. PLN",
                f"źródło danych finansowych: {'raport/ESPI/ESEF (pierwotne)' if c['zrodlo_fin']=='pierwotne' else 'agregator danych z KRS - wymaga weryfikacji w RDF'}",
                f"zysk brutto ze sprzedaży: {fmt(c['zysk_brutto_sprz'])}",
                f"EBIT: {fmt(c['ebit'])}",
                f"EBITDA: {fmt(c['ebitda'])}" + (f" ({c['ebitda_uwagi']})" if c['ebitda_uwagi'] else ""),
                f"data publikacji: {c['data_pub']}",
                f"plik lokalny: {c['plik'] or 'brak (PDF niedostępny)'}",
                c["uwagi"],
            ]
            w.writerow([
                c["nazwa"], c["krs"], c["nip"], c["regon"], c["siedziba"], c["www"], c["kategoria"], c["opis"],
                c["budownictwo"], c["rok"], c["przychody"], fmt(c["zysk_netto"]),
                f"{m:.1f}%" if m is not None else NIE, c["waluta"], c["typ"], rj(c["krs"]), c["link_raportu"],
                " | ".join(extra),
            ])
    return path


# ---------------------------------------------------------------- wykresy
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
HATCH = "////"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK, "figure.facecolor": SURF, "axes.facecolor": SURF,
    "hatch.color": "white", "hatch.linewidth": 0.8,
})


def short(n):
    return (n.split(" (")[0].replace(" sp. z o.o. sp.k.", "").replace(" sp. z o.o.", "").replace(" S.A.", "")
            .replace(" sp. j.", "").replace("Asseco Business Solutions", "Asseco BS"))


def label(c):
    s = short(c["nazwa"])
    if not c["rok"].startswith("2025") or "/" in c["rok"] or "prawdop" in c["rok"]:
        y = {"2025/26 (01.04.2025-31.03.2026)": "FY25/26", "01.10.2024-30.09.2025": "FY24/25",
             "2025 (prawdopodobnie - wg etykiety rejestr.io)": "2025?"}.get(c["rok"], c["rok"])
        s += f" ({y})"
    if c["zrodlo_fin"] == "agregator":
        s += " *"
    return s


def style_ax(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)


def legend_src(ax, color, loc="lower right"):
    ax.legend(handles=[Patch(facecolor=color, label="dane z raportu / ESPI / ESEF"),
                       Patch(facecolor=color, hatch=HATCH, label="* dane z agregatora KRS (do weryfikacji)")],
              loc=loc, frameon=False, fontsize=9)


def hbar(ax, rows, key, color, unit=1000.0):
    ys = range(len(rows))
    vals = [r[key] / unit for r in rows]
    bars = ax.barh(list(ys), vals, color=color, height=0.68, edgecolor=SURF, linewidth=1.5)
    for b, r in zip(bars, rows):
        if r["zrodlo_fin"] == "agregator":
            b.set_hatch(HATCH)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([label(r) for r in rows])
    ax.invert_yaxis()
    span = max(abs(v) for v in vals)
    for y, v in zip(ys, vals):
        txt = (f"{v:,.1f}" if abs(v) >= 0.1 else f"{v:.3f}").replace(",", " ").replace(".", ",")
        ax.text(v + (span * 0.01 if v >= 0 else -span * 0.01), y, txt, va="center",
                ha="left" if v >= 0 else "right", fontsize=8.5, color=INK2)
    return span


def chart_revenue():
    rows = sorted(COMPANIES, key=lambda c: c["przychody"], reverse=True)
    fig, ax = plt.subplots(figsize=(11, 8.5))
    span = hbar(ax, rows, "przychody", BLUE)
    ax.set_xlim(0, span * 1.12)
    style_ax(ax)
    ax.set_xlabel("mln PLN")
    ax.set_title("Przychody ze sprzedaży – ostatni pełny rok obrotowy (dane jednostkowe, mln PLN)",
                 loc="left", fontsize=13, color=INK, pad=12)
    legend_src(ax, BLUE)
    fig.text(0.01, 0.01, "Rok 2025, chyba że zaznaczono inaczej. Asseco Poland i Asseco BS: przychody operacyjne MSSF. "
             "Źródła: raporty roczne, ESPI/ESEF, rejestr.io/bizraport (KRS).", fontsize=8, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    p = os.path.join(HERE, "charts", "przychody_spolek.png")
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def chart_profit():
    rows = sorted([c for c in COMPANIES if c["zysk_netto"] is not None], key=lambda c: c["zysk_netto"], reverse=True)
    fig, ax = plt.subplots(figsize=(11, 8.5))
    span = hbar(ax, rows, "zysk_netto", ORANGE)
    lo = min(r["zysk_netto"] for r in rows) / 1000
    ax.set_xlim(min(0, lo) - span * 0.15, span * 1.12)
    ax.axvline(0, color=INK2, linewidth=0.8)
    style_ax(ax)
    ax.set_xlabel("mln PLN")
    ax.set_title("Zysk (strata) netto – ostatni pełny rok obrotowy (dane jednostkowe, mln PLN)",
                 loc="left", fontsize=13, color=INK, pad=12)
    legend_src(ax, ORANGE)
    fig.text(0.01, 0.01, "Pominięto Soneta (enova365) – zysk netto 2025 nie ustalono. Asseco Poland: zysk netto zawiera dywidendy od spółek zależnych.",
             fontsize=8, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    p = os.path.join(HERE, "charts", "zysk_netto_spolek.png")
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def chart_combined():
    rows = sorted(COMPANIES, key=lambda c: c["przychody"], reverse=True)
    big = [r for r in rows if r["przychody"] >= 100000]
    small = [r for r in rows if r["przychody"] < 100000]
    fig, axes = plt.subplots(1, 2, figsize=(15, 8.5), gridspec_kw={"width_ratios": [1, 1]})
    for ax, grp, ttl in ((axes[0], big, "Przychody ≥ 100 mln PLN"), (axes[1], small, "Przychody < 100 mln PLN (inna skala)")):
        ys = list(range(len(grp)))
        h = 0.38
        rev = [r["przychody"] / 1000 for r in grp]
        net = [(r["zysk_netto"] or 0) / 1000 for r in grp]
        b1 = ax.barh([y - h / 2 for y in ys], rev, height=h, color=BLUE, edgecolor=SURF, linewidth=1)
        b2 = ax.barh([y + h / 2 for y in ys], net, height=h, color=ORANGE, edgecolor=SURF, linewidth=1)
        for bars, src in ((b1, grp), (b2, grp)):
            for b, r in zip(bars, src):
                if r["zrodlo_fin"] == "agregator":
                    b.set_hatch(HATCH)
        span = max(rev)
        for y, v, r in zip(ys, net, grp):
            m = margin(r)
            t = "zysk n/d" if r["zysk_netto"] is None else (f"marża {m:.1f}%" if abs(m) >= 0.05 else f"marża {m:.2f}%").replace(".", ",")
            ax.text(max(v, 0) + span * 0.01, y + h / 2, t, va="center", fontsize=8, color=INK2)
        for y, v in zip(ys, rev):
            ax.text(v + span * 0.01, y - h / 2, f"{v:,.0f}".replace(",", " "), va="center", fontsize=8, color=INK2)
        ax.set_yticks(ys)
        ax.set_yticklabels([label(r) for r in grp])
        ax.invert_yaxis()
        ax.axvline(0, color=INK2, linewidth=0.8)
        lo = min(net + [0])
        ax.set_xlim(lo - span * 0.05 if lo < 0 else 0, span * 1.18)
        style_ax(ax)
        ax.set_xlabel("mln PLN")
        ax.set_title(ttl, loc="left", fontsize=11, color=INK)
    fig.suptitle("Przychody vs zysk netto (dane jednostkowe, mln PLN) – posortowane wg przychodów",
                 x=0.01, ha="left", fontsize=13, color=INK)
    fig.legend(handles=[Patch(facecolor=BLUE, label="Przychody"), Patch(facecolor=ORANGE, label="Zysk (strata) netto"),
                        Patch(facecolor="#bbbbbb", hatch=HATCH, label="* dane z agregatora KRS (do weryfikacji)")],
               loc="upper right", ncol=3, frameon=False, fontsize=9)
    fig.text(0.01, 0.01, "Jedna oś na panel; dwa panele mają różne skale, aby mniejsze spółki były czytelne. Etykieta przy pomarańczowym słupku = marża netto.",
             fontsize=8, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    p = os.path.join(HERE, "charts", "przychody_i_zysk_netto.png")
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "charts"), exist_ok=True)
    print(write_csv())
    print(chart_revenue())
    print(chart_profit())
    print(chart_combined())
    for c in sorted(COMPANIES, key=lambda c: c["przychody"], reverse=True):
        m = margin(c)
        print(f"{short(c['nazwa']):28s} {c['rok'][:10]:10s} {c['przychody']:>10} {fmt(c['zysk_netto']):>10} {('%.1f%%' % m) if m is not None else NIE:>8} {c['zrodlo_fin']}")
