# 🧪 Dyad Integration Testing Framework

Comprehensive testing suite for the Dyad integration, covering asset generation quality, correctness, and performance using GPT as an auto-rater.

## 🎯 Testing Objectives

### 1. Asset Generation Correctness
- **Text Content**: Verify brand data is correctly extracted and applied
- **Fonts**: Ensure proper font application throughout the document
- **Images**: Validate image generation and integration
- **Colors**: Check brand color consistency
- **Layout**: Verify proper HTML structure and CSS

### 2. Asset Quality Assessment
- **HTML Quality**: Code structure, semantic markup, best practices
- **Content Relevance**: Brand alignment, message consistency
- **Visual Appeal**: Design quality, user experience
- **Accessibility**: Alt text, semantic tags, responsive design
- **Professional Standards**: Industry best practices compliance

## 🚀 Quick Start

### Run All Tests
```bash
pnpm test:comprehensive
```

### Run Quick Tests
```bash
pnpm test:quick
```

### Generate Quality Report
```bash
pnpm evaluate:report data/drafts/gigit/test.html data/brands/gigit.json
```

## 📋 Test Categories

### Phase 1: System Health Checks
- ✅ Node.js version compatibility
- ✅ pnpm availability
- ✅ Python availability
- ✅ Environment file (.env)
- ✅ Required directories
- ✅ Required files

### Phase 2: Asset Generation Tests
- ✅ Brand data loading
- ✅ Template resolution
- ✅ HTML generation
- ✅ PDF generation
- ✅ Image generation

### Phase 3: Quality Assessment Tests
- ✅ Font application
- ✅ Content accuracy
- ✅ Visual design
- ✅ Accessibility
- ✅ GPT evaluation

### Phase 4: Integration Tests
- ✅ CLI integration
- ✅ SSR workflow
- ✅ File sync
- ✅ End-to-end workflow

### Phase 5: Performance Tests
- ✅ Generation speed
- ✅ Memory usage
- ✅ File sizes

## 🔍 GPT Asset Evaluator

The GPT Asset Evaluator uses OpenAI's GPT-5 to automatically assess asset quality:

### Features
- **HTML Quality**: Evaluates code structure, semantic markup, CSS organization
- **Content Relevance**: Assesses brand alignment and message consistency
- **Visual Appeal**: Analyzes design quality and user experience
- **Overall Quality**: Comprehensive evaluation across all dimensions

### Usage Examples

#### Evaluate Single File
```bash
pnpm evaluate:single data/drafts/gigit/test.html
```

#### Generate Quality Report
```bash
pnpm evaluate:report data/drafts/gigit/test.html data/brands/gigit.json
```

#### Batch Evaluation
```bash
pnpm evaluate:batch data/drafts/gigit/
```

### Evaluation Criteria

#### HTML Quality (1-10)
1. Code structure and organization
2. Semantic HTML usage
3. CSS organization and best practices
4. Responsive design implementation
5. Accessibility features

#### Content Relevance (1-10)
1. Brand name consistency
2. Message alignment
3. Tone consistency
4. Value proposition clarity
5. Content accuracy

#### Visual Appeal (1-10)
1. Color scheme and contrast
2. Typography and readability
3. Layout and spacing
4. Visual hierarchy
5. Modern design principles

## 📊 Test Reports

### Comprehensive Test Report
Located at: `tests/comprehensive_test_report.json`

Contains:
- Test execution timestamp
- Duration statistics
- Overall success rate
- Detailed results by category
- Individual test outcomes

### Quality Assessment Report
Located at: `data/drafts/gigit/*_quality_report.json`

Contains:
- GPT evaluation scores
- Detailed analysis
- Recommendations for improvement
- Quality metrics breakdown

## 🛠️ Test Configuration

### Environment Variables
```bash
# Required for GPT evaluation
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Customize test behavior
TEST_TIMEOUT=30000
TEST_VERBOSE=true
```

### Test Thresholds
- **Font Application**: 100% (all checks must pass)
- **Content Accuracy**: 100% (all checks must pass)
- **Visual Design**: 75% (3 out of 4 checks)
- **Accessibility**: 80% (4 out of 5 checks)
- **Overall Quality**: 7.0/10 minimum score

## 🔧 Customizing Tests

### Adding New Test Categories
1. Create test method in `ComprehensiveTestRunner`
2. Add to appropriate phase in `runAllTests()`
3. Implement test logic with proper error handling
4. Return standardized result format

### Example Test Method
```javascript
async testCustomFeature() {
  try {
    // Test implementation
    const result = await someTest();
    
    return {
      success: result.success,
      message: result.message,
      details: result.details || {}
    };
  } catch (error) {
    return {
      success: false,
      message: `Error: ${error.message}`
    };
  }
}
```

### Modifying GPT Evaluation
1. Update prompts in `GPTAssetEvaluator`
2. Adjust evaluation criteria
3. Modify scoring algorithms
4. Add new evaluation dimensions

## 📈 Performance Monitoring

### Metrics Tracked
- **Generation Time**: Total time for asset creation
- **File Sizes**: HTML, PDF, and image file sizes
- **Memory Usage**: Peak memory consumption
- **API Response Times**: GPT evaluation latency

### Performance Thresholds
- **HTML Generation**: < 30 seconds
- **PDF Generation**: < 60 seconds
- **File Size**: HTML > 10KB, PDF > 100KB
- **Memory Usage**: < 512MB peak

## 🐛 Troubleshooting

### Common Issues

#### Test Failures
1. Check environment setup
2. Verify required dependencies
3. Ensure test data availability
4. Check API key configuration

#### GPT Evaluation Errors
1. Verify OpenAI API key
2. Check API rate limits
3. Ensure internet connectivity
4. Validate prompt formatting

#### Performance Issues
1. Monitor system resources
2. Check file system permissions
3. Verify network connectivity
4. Review timeout configurations

### Debug Mode
Enable verbose logging:
```bash
TEST_VERBOSE=true pnpm test:comprehensive
```

## 📚 API Reference

### ComprehensiveTestRunner
Main test orchestrator class with methods:
- `runAllTests()`: Execute all test phases
- `runSystemHealthChecks()`: System validation
- `runAssetGenerationTests()`: Asset creation tests
- `runQualityAssessmentTests()`: Quality evaluation
- `runIntegrationTests()`: Integration validation
- `runPerformanceTests()`: Performance measurement
- `generateFinalReport()`: Generate comprehensive report

### GPTAssetEvaluator
AI-powered quality assessment with methods:
- `evaluateHTMLQuality()`: HTML code quality
- `evaluateContentRelevance()`: Brand alignment
- `evaluateVisualAppeal()`: Design quality
- `evaluateOverallQuality()`: Comprehensive assessment
- `generateQualityReport()`: Detailed quality report

## 🤝 Contributing

### Adding Tests
1. Follow existing test patterns
2. Include proper error handling
3. Add comprehensive documentation
4. Update this README

### Improving Evaluations
1. Enhance GPT prompts
2. Add new evaluation criteria
3. Optimize scoring algorithms
4. Expand test coverage

## 📄 License

This testing framework is part of the Eigen-UI project and follows the same licensing terms.

## 🆘 Support

For issues or questions:
1. Check troubleshooting section
2. Review test logs and reports
3. Verify environment configuration
4. Consult project documentation
