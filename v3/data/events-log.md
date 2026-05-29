# TradingApp v3 — Events log

Source : pipeline RSS + DeepSeek (schéma 7 champs).
Append-only. Édité par v3/scripts/agent_news.py (GitHub Actions cron).

| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id |
|---|---|---|---|---|---|---|---|---|---|---|
<!-- batch 2026-05-29T14:39:49Z : 50 events -->
| 2026-05-29 | Tech-IA | Blue Origin | Blue Origin rocket explodes on Florida launch pad, Jeff Bezos calls it 'very rough day' |  | intraday | 1 | bbc_business | US | other |  |
| 2026-05-28 | Énergie-Matières-premières | Café | Le prix du café dans certains centres-villes atteint £5, reflétant l'impact des tarifs, du climat, des goûts culturels de la génération Z et des stratégies de marché des producteurs. | Café (KC=F) | jours | 1 | bbc_business | Global | commodity |  |
| 2026-05-28 | Énergie-Matières-premières | Pétrole-EIA | Report of breakthrough in US-Iran talks with extended ceasefire subject to Trump's approval, causing oil prices to fall. | Brent (BZ=F), WTI (CL=F) | intraday | 1 | bbc_business | Moyen-Orient | geopolitical |  |
| 2026-05-28 | Earnings-Corporate | Insider Trading | Google employee charged with insider trading using internal data to make $1.2m on bets | Alphabet (GOOGL) | intraday | 1 | bbc_business | US | regulatory |  |
| 2026-05-27 | Commerce-Tariffs | Automobile-Chine | Les constructeurs automobiles mondiaux peinent à concurrencer la Chine, qui domine les écosystèmes des véhicules électriques. | Tesla (TSLA), Stellantis (STLA), Volkswagen (VOW3.DE) | jours | 1 | bbc_business | Global | sector |  |
| 2026-05-27 | Énergie-Matières-premières | Pétrole-Gaz | UK energy price cap raised by £221/year due to Iran war impact on energy markets | UK Natural Gas (NG=F), Brent (BZ=F) | intraday | 1 | bbc_business | EU | commodity |  |
| 2026-05-27 | Earnings-Corporate | Automotive | Ferrari unveils first fully electric car, Luce model, shares slump | Ferrari (RACE) | intraday | 1 | bbc_business | EU | sector |  |
| 2026-05-27 | Tech-IA | Semi-conducteurs | SK Hynix et Micron rejoignent le club des 1000 milliards de dollars de capitalisation grâce à la demande de puces IA | SK Hynix (000660.KS), Micron (MU) | intraday | 1 | bbc_business | Global | sector |  |
| 2026-05-27 | Tech-IA | IA-Sécurité | Ethical hacker warns AI tools like Mythos will increase competition difficulty |  | intraday | 1 | bbc_business | Global | sector |  |
| 2026-05-27 |  |  | The rise of the fruit that tastes like custard |  |  | 1 | bbc_business |  | other |  |
| 2026-05-18 | Earnings-Corporate | Amazon | Amazon's dominance over Western online retail rivals highlighted | Amazon (AMZN) | intraday | 1 | bbc_business | US | sector |  |
| 2026-05-13 | Tech-IA | Smart glasses | Meta's smart glasses selling better than ever despite privacy concerns | Meta (META) | intraday | 1 | bbc_business | US | sector |  |
| 2026-05-29 | Énergie-Matières-premières | Énergie | Power NI et Firmus augmentent leurs tarifs en raison de la hausse des prix mondiaux de l'énergie et du gaz. | Gaz naturel (NG=F) | intraday | 1 | bbc_business | EU | commodity |  |
| 2026-05-27 | Énergie-Matières-premières | Café | Mauvaises récoltes de café au Brésil et au Vietnam font grimper les prix | Café (KC=F) | jours | 1 | bbc_business | Global | commodity |  |
| 2026-05-27 |  |  | 'I fear for my son's farming future due to costs' |  |  | 1 | bbc_business |  | other |  |
| 2026-03-28 | Énergie-Matières-premières | Agri-softs | Orange juice price surge to £5.30 per unit, reflecting broader commodity inflation in butter, chocolate, coffee, milk. | Orange Juice (OJ=F) | intraday | 1 | bbc_business | Global | commodity |  |
| 2026-05-27 | Énergie-Matières-premières | Pétrole-Énergie | Household energy prices to rise 13% in July due to soaring wholesale costs from US-Israel war with Iran. | Brent (BZ=F), WTI (CL=F) | intraday | 1 | bbc_business | Global | geopolitical |  |
| 2026-05-29 | Géopolitique | Iran-Moyen-Orient | US VP Vance says US and Iran 'very close' to deal but 'not there yet'; framework of ceasefire extension agreed pending approval. | Pétrole brut (CL=F) | intraday | 1 | bbc_world | Moyen-Orient | geopolitical |  |
| 2026-05-29 | Géopolitique | Iran-Moyen-Orient | Netanyahu ordonne à l'armée israélienne d'étendre le contrôle de Gaza à 70%, en violation du cessez-le-feu d'octobre 2025. | Pétrole brut (CL=F) | intraday | 1 | bbc_world | Moyen-Orient | geopolitical |  |
| 2026-05-28 | Géopolitique | Iran-Moyen-Orient | Strike on Gaza City hospitals kills several, including children, targeting Hamas commander | Pétrole (CL=F) | intraday | 1 | bbc_world | Moyen-Orient | geopolitical |  |
| 2026-05-28 | Géopolitique | Iran-Moyen-Orient | Israel hits Lebanese capital in 'targeted strike', breaking ceasefire with Hezbollah. | Brent (BZ=F) | intraday | 1 | bbc_world | Moyen-Orient | geopolitical |  |
| 2026-05-28 | Géopolitique | Iran-Moyen-Orient | Hezbollah uses fibre-optic drones against Israel, learning from Ukraine war |  | intraday | 1 | bbc_world | Moyen-Orient | geopolitical |  |
| 2026-05-28 | Géopolitique | Philippines | Le procès de Duterte devant la CPI commence le 30 novembre pour la guerre contre la drogue. |  | jours | 1 | bbc_world | Global | geopolitical |  |
| 2026-05-28 |  |  | How did this novel about food win a Booker Prize this year? |  |  | 1 | bbc_world |  | other |  |
| 2026-05-29 | Earnings-Corporate | Dell Technologies | Dell reported AI server revenue soaring 757% YoY, fastest revenue growth since 2018, stock up 32%. | Dell (DELL) | intraday | 1 | cnbc_top | US | earnings |  |
| 2026-05-29 | Tech-IA | SpaceX | Elon Musk comments on SpaceX-Anthropic deal diverge from IPO filing, raising concerns among skeptics. |  | intraday | 1 | cnbc_top | US | regulatory |  |
| 2026-05-29 | Tech-IA | Nvidia | Nvidia invests billions into photonics technology for more efficient data transfer, potentially crucial for AI. | Nvidia (NVDA) | intraday | 1 | cnbc_top | US | sector |  |
| 2026-05-29 |  |  | There's a record disconnect unfolding in the trading pits right now |  |  | 1 | cnbc_top |  | other |  |
| 2026-05-29 | Banques-centrales | Fed-FOMC | Fed Governor Bowman warns against hiking rates due to inflation spike from energy prices and tariffs. | US Dollar Index (DX-Y.NYB) | intraday | 1 | cnbc_top | US | central_bank_subtle |  |
| 2026-05-28 | Énergie-Matières-premières | Pétrole-EIA | Exxon executive warns oil inventories will hit dangerously low levels in weeks, forcing Brent prices to spike to $150-$160/barrel. | Brent (BZ=F) | intraday | 1 | cnbc_top | Global | commodity |  |
| 2026-05-29 | Énergie-Matières-premières | Pétrole-EIA | Oil drops 20% from 2026 peak on optimism over U.S.-Iran ceasefire talks, hopes for Strait of Hormuz reopening. | Brent (BZ=F) | intraday | 1 | cnbc_top | Moyen-Orient | geopolitical |  |
| 2026-05-29 | Tech-IA | IA-Action | Dan Ives prédit que la croissance d'Anthropic n'est que le début du rallye IA et que le Nasdaq atteindra 30 000 points d'ici 2027. | Nasdaq (^IXIC) | intraday | 1 | cnbc_top | US | sector |  |
| 2026-05-29 | Géopolitique | Iran-Moyen-Orient | Trump administration threatens sanctions and military action against Oman, a longtime ally. | Pétrole brut (CL=F) | intraday | 1 | cnbc_top | Moyen-Orient | geopolitical |  |
| 2026-05-29 | Tech-IA | Régulation IA | EU seeks to intensify talks with U.S. on advanced cyber AI models amid concerns over Anthropic's Mythos model |  | intraday | 1 | cnbc_top | EU | regulatory |  |
| 2026-05-28 | Géopolitique | Iran-Moyen-Orient | Iran reportedly launches missiles as Trump mulls deal to pause war for two months | Brent (BZ=F) | intraday | 1 | cnbc_top | Moyen-Orient | geopolitical |  |
| 2026-05-28 | Earnings-Corporate | Costco | Costco reports record-breaking gas volumes and rising fuel prices driving first-time members to its stations. | Costco (COST) | intraday | 1 | cnbc_top | US | earnings |  |
| 2026-05-28 | Earnings-Corporate | Retail | Gap cuts sales guidance after Old Navy underperforms, shares fall 14% | Gap (GPS) | intraday | 1 | cnbc_top | US | earnings |  |
| 2026-05-29 | Earnings-Corporate | Tesla | Tesla registered 42 automated vehicles for Robotaxi service in Texas, far behind Waymo's fleet size. | Tesla (TSLA) | intraday | 1 | cnbc_top | US | sector |  |
| 2026-05-28 | Earnings-Corporate | Okta | Okta jumps 8% after beating Q1 estimates, CEO cites agentic AI demand and increased AI investment. | Okta (OKTA) | intraday | 1 | cnbc_top | US | earnings |  |
| 2026-05-29 | Tech-IA | Semi-conducteurs | Samsung Electronics a commencé à expédier des échantillons de puces mémoire HBM4E de nouvelle génération à ses clients dans le monde entier. | Samsung Electronics (005930.KS) | intraday | 1 | cnbc_top | Global | sector |  |
| 2026-05-28 | Tech-IA |  | Jim Cramer identifies three mistakes preventing investors from capturing AI winners |  | intraday | 1 | cnbc_top | US | other |  |
| 2026-05-29 | Earnings-Corporate | Biotech-Pharma | Innovent Biologics shares rise 10% after entering a strategic global licensing and collaboration agreement with Pfizer to develop oncology medicines, with deal value up to $10.5 billion. | Innovent Biologics (1801.HK) | intraday | 1 | cnbc_top | CN | m_a |  |
| 2026-05-28 | Tech-IA | Valuation-Funding | Anthropic surpasses OpenAI as most valuable AI startup, nearing $1 trillion valuation after $65 billion funding round. | Anthropic (private) | intraday | 1 | cnbc_top | US | sector |  |
| 2026-05-29 | Earnings-Corporate | LG Electronics | LG Electronics shares surge 24% after unveiling automotive innovations using Google technology | LG Electronics (KRX: 066570) | intraday | 1 | cnbc_top | Global | sector |  |
| 2026-05-29 | Géopolitique | Iran-Moyen-Orient | Asia-Pacific markets rise as investors shrug off renewed Iran tensions amid ceasefire optimism | Kospi (^KS11), Topix (^TOPX) | intraday | 1 | cnbc_top | Global | geopolitical |  |
| 2026-05-29 | Géopolitique | Iran-Moyen-Orient | Mental scars from past inflation and geopolitical shocks amid Iran war reinforce stagflation fears |  | intraday | 1 | cnbc_economy | Moyen-Orient | geopolitical |  |
| 2026-05-28 | Macro-indicateurs | PCE-Inflation | Core PCE inflation at 3.3% annual rate in April, in line with expectations | US Dollar Index (DX-Y.NYB), S&P 500 (^GSPC) | intraday | 1 | cnbc_economy | US | macro |  |
| 2026-05-28 | Banques-centrales | Fed-FOMC | Fed's Goolsbee says energy inflation more persistent than expected, notes oil prices still high despite potential US-Iran peace deal | Pétrole (CL=F) | intraday | 1 | cnbc_economy | US | central_bank_subtle |  |
| 2026-05-28 | Banques-centrales | Fed-FOMC | Minneapolis Fed President Kashkari says inflation fight takes priority, labor market is 'in decent shape', warns high inflation risks becoming embedded in expectations. | S&P 500 (^GSPC), DXY (DX-Y.NYB) | intraday | 1 | cnbc_economy | US | central_bank_subtle |  |
| 2026-05-26 | Banques-centrales | BCE | Le gouverneur de la Banque de France déclare que la BCE 'fera ce qui est nécessaire' pour maîtriser l'inflation, les marchés anticipent une hausse des taux. | EUR/USD (EUR=X) | intraday | 1 | cnbc_economy | EU | central_bank_subtle |  |
