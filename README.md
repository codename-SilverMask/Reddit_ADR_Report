# Reddit ADR Analyzer

A specialized Python tool that identifies and analyzes Adverse Drug Reactions (ADRs) from ADHD-related subreddits. The analyzer scrapes posts and comments, uses NLP pattern matching to detect medication mentions and side effects, performs sentiment analysis, and generates comprehensive visualizations.

## Features

- 🔍 **Automated Reddit Scraping** - Collects posts and comments from multiple ADHD subreddits
- 💊 **Medication Detection** - Identifies 143+ medications including brand names, generics, and slang terms
- 🧠 **ADR Pattern Matching** - Context-window based NLP extraction around medication mentions
- 📊 **Sentiment Analysis** - Calculates sentiment scores for medication experiences
- 📈 **Comprehensive Visualizations** - Generates 6 different analytical charts
- 📁 **Multi-format Export** - Outputs data in JSON and CSV formats

## Installation

### Prerequisites

- Python 3.7+
- Reddit API credentials (OAuth2)

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd redditPaginationADR
```

2. Create and activate a virtual environment:

```bash
python -m venv ADRenv
# Windows:
ADRenv\Scripts\activate
# macOS/Linux:
source ADRenv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure Reddit API credentials:
   - Edit `reddit_adr_analyzer.py` (lines 16-19)
   - Replace with your Reddit API credentials

## Usage

### Basic Usage

```bash
python reddit_adr_analyzer.py
```

### Custom Subreddits

```bash
python reddit_adr_analyzer.py -s "ADHD,ADHDmemes,adhdwomen"
```

### Custom Output Directory

```bash
python reddit_adr_analyzer.py -o my_analysis
```

### Skip Visualizations (Faster)

```bash
python reddit_adr_analyzer.py --no-visualizations
```

## Output Structure

After running the analyzer, the following files are generated:

```
adr_analysis_output/
├── raw_posts.json              # All scraped posts
├── raw_comments.json           # All scraped comments
├── adr_mentions.json           # Extracted ADR records
├── adr_mentions.csv            # ADR records in CSV format
├── summary_statistics.json     # Aggregated metrics
└── visualizations/             # PNG charts
    ├── adr_timeline.png
    ├── adr_categories.png
    ├── symptom_heatmap.png
    ├── severity_distribution.png
    ├── sentiment_analysis.png
    └── monthly_trend.png
```

## Analysis Report

### Summary Statistics

- **Total ADR Mentions**: 8,803
- **Unique Medications Analyzed**: 143
- **Date Range**: September 26, 2022 - January 17, 2026
- **Data Sources**:
  - Comments: 6,171 (70.1%)
  - Posts: 2,632 (29.9%)

### Top 10 Medications by ADR Mentions

| Rank | Medication      | Mentions |
| ---- | --------------- | -------- |
| 1    | Vyvanse         | 2,742    |
| 2    | Adderall        | 1,032    |
| 3    | Concerta        | 417      |
| 4    | Ritalin         | 388      |
| 5    | Wellbutrin      | 320      |
| 6    | Guanfacine      | 262      |
| 7    | Methylphenidate | 225      |
| 8    | Strattera       | 193      |
| 9    | Lexapro         | 139      |
| 10   | Zoloft          | 117      |

### Severity Distribution

- **Moderate**: 1,728 mentions (58.0%)
- **Severe**: 851 mentions (28.6%)
- **Mild**: 404 mentions (13.4%)

### Most Common Symptoms

Top 10 reported symptoms:

1. Anxiety (1,980 mentions)
2. Side effects (963 mentions)
3. Rash (658 mentions)
4. Crash (595 mentions)
5. Depression (527 mentions)
6. Fatigue/Tired (356 mentions)
7. Anxious (348 mentions)
8. Emotional instability (311 mentions)
9. Heart rate issues (305 mentions)
10. Panic attacks (257 mentions)

### ADR Categories Distribution

- **Psychological Symptoms**: 4,388 (49.9%)
- **Physical Symptoms**: 2,761 (31.4%)
- **Side Effect Indicators**: 2,466 (28.0%)
- **Withdrawal/Tolerance**: 1,941 (22.1%)
- **Cardiovascular**: 514 (5.8%)
- **Cognitive**: 251 (2.9%)
- **Neurological**: 31 (0.4%)
- **Gastrointestinal**: 19 (0.2%)

### Average Sentiment Score: -1.0

The predominantly negative sentiment indicates that most mentions occur in the context of adverse reactions rather than positive experiences.

## Visualizations

### ADR Mentions Over Time

![ADR Timeline](adr_analysis_output/visualizations/adr_timeline.png)
_Timeline showing ADR mentions over time for the top 10 medications_

### Most Common ADR Categories

![ADR Categories](adr_analysis_output/visualizations/adr_categories.png)
_Bar chart of the 15 most frequently mentioned ADR categories_

### Symptom Heatmap by Medication

![Symptom Heatmap](adr_analysis_output/visualizations/symptom_heatmap.png)
_Heatmap showing the relationship between top medications and common symptoms_

### ADR Severity Distribution

![Severity Distribution](adr_analysis_output/visualizations/severity_distribution.png)
_Distribution of ADR mentions by severity level (severe, moderate, mild)_

### Sentiment Analysis by Medication

![Sentiment Analysis](adr_analysis_output/visualizations/sentiment_analysis.png)
_Box plot showing sentiment score distribution for top 10 medications_

### Overall Monthly Trend

![Monthly Trend](adr_analysis_output/visualizations/monthly_trend.png)
_Aggregate trend of all ADR mentions over time_

## Technical Details

### NLP Pattern Matching

- **Context Window**: ±200 characters around medication mentions
- **Word Boundaries**: Regex pattern matching with `\b` to avoid partial matches
- **Multi-level Detection**: Medication → ADR indicators → Symptoms → Severity

### Rate Limiting

- 2 second delay between post requests
- 1 second delay between comment fetches
- Safety limit of 800 iterations per subreddit

### Data Processing Pipeline

1. OAuth2 authentication with Reddit API
2. Paginated scraping using `after` cursors
3. Context-window based ADR extraction
4. Sentiment scoring using keyword ratios
5. Statistical aggregation and visualization generation

## Supported Medication Categories

- **Stimulants**: Adderall, Vyvanse, Ritalin, Concerta, etc.
- **Non-stimulants**: Strattera, Wellbutrin, Intuniv, etc.
- **Antidepressants**: Prozac, Zoloft, Lexapro, Cymbalta, etc.
- **Anxiety Medications**: Xanax, Ativan, Buspar, etc.
- **Mood Stabilizers**: Abilify, Seroquel, Lithium, etc.
- **Alternative Substances**: Cannabis, psilocybin, LSD
- **Slang Terms**: Addy, happy pills, brain meds, study meds, etc.

## Known Limitations

1. **Simple NLP**: Keyword-based matching may miss complex ADR descriptions or generate false positives
2. **Memory Intensive**: All data held in memory; large datasets may cause issues
3. **No Resume Capability**: Crashes require full restart from beginning
4. **Hardcoded Credentials**: API credentials in source code (not production-ready)
5. **No Deduplication**: Same post/comment may be processed multiple times

## Contributing

Contributions are welcome! Areas for improvement:

- More sophisticated NLP/ML models for ADR detection
- Database integration for large-scale data storage
- Real-time streaming analysis
- Enhanced visualization options
- Credential management via environment variables

## License

[Add your license here]

## Disclaimer

This tool is for research and educational purposes only. The data collected should not be used for medical diagnosis or treatment decisions. Always consult healthcare professionals for medical advice.

## Support

For issues, questions, or suggestions, please open an issue in the repository.
