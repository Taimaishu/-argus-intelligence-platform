# Contributing to Argus Intelligence Platform

Thank you for your interest in contributing to Argus! This document provides guidelines and workflows for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment
- Report inappropriate behavior to maintainers

## Getting Started

### Prerequisites
- Python 3.13+
- Node.js 20+
- Ollama (optional, for local LLM)
- Git

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/-argus-intelligence-platform.git
   cd -argus-intelligence-platform
   ```

2. **Backend setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8  # Dev dependencies
   ```

3. **Frontend setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Run tests**
   ```bash
   # Backend
   cd backend
   pytest

   # Frontend
   cd frontend
   npm test
   ```

## Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Code refactoring
- `test/` - Adding tests

### 2. Make Changes

**Backend (Python)**
- Follow PEP 8 style guide
- Run `black app` for formatting
- Run `flake8 app` for linting
- Add docstrings to functions/classes
- Write unit tests for new code

**Frontend (TypeScript)**
- Follow existing code style
- Run `npm run lint` before committing
- Ensure TypeScript types are correct
- Add comments for complex logic

### 3. Write Tests

**Backend Tests**
```python
# backend/tests/test_your_feature.py
import pytest

def test_your_feature():
    # Arrange
    # Act
    # Assert
    assert True
```

**Frontend Tests**
```typescript
// frontend/src/__tests__/YourComponent.test.tsx
import { render, screen } from '@testing-library/react';
import { YourComponent } from '../components/YourComponent';

test('renders correctly', () => {
  render(<YourComponent />);
  expect(screen.getByText('Expected Text')).toBeInTheDocument();
});
```

### 4. Run Tests Locally

```bash
# Backend
cd backend
pytest tests/ -v --cov=app

# Frontend
cd frontend
npm run build  # Ensure it builds
npm test      # Run tests if available
```

### 5. Commit Changes

Use conventional commit messages:
```bash
git commit -m "feat: add OSINT artifact extraction"
git commit -m "fix: resolve memory leak in canvas"
git commit -m "docs: update installation instructions"
git commit -m "test: add tests for document processor"
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Description of what was changed and why
- Screenshots (if UI changes)
- Link to related issue (if applicable)

## Pull Request Guidelines

### PR Checklist
- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow conventions
- [ ] No merge conflicts
- [ ] PR description is clear and complete

### PR Review Process
1. Automated CI checks must pass
2. At least one maintainer review required
3. Address review comments
4. Squash commits if requested
5. Maintainer will merge when approved

## Testing Guidelines

### Backend Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_document_processor.py -v

# Run specific test
pytest tests/test_api.py::test_health_endpoint -v
```

### Frontend Testing
```bash
# Build check
npm run build

# Lint check
npm run lint

# Type check
npx tsc --noEmit
```

## Code Style

### Python (Backend)
```python
# Good
def process_document(file_path: str, options: Dict[str, Any]) -> ProcessResult:
    """
    Process a document and extract text.

    Args:
        file_path: Path to the document
        options: Processing options

    Returns:
        ProcessResult with extracted text and metadata
    """
    # Implementation
    pass

# Use type hints
# Add docstrings
# Follow PEP 8
```

### TypeScript (Frontend)
```typescript
// Good
interface DocumentUploadProps {
  onUpload: (file: File) => Promise<void>;
  maxSize?: number;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUpload,
  maxSize = 50 * 1024 * 1024
}) => {
  // Implementation
};

// Use TypeScript types
// Descriptive names
// Functional components
```

## Adding New Features

### Backend Feature
1. Create service in `backend/app/core/`
2. Add API route in `backend/app/api/routes/`
3. Update OpenAPI docs
4. Write tests in `backend/tests/`
5. Update README if user-facing

### Frontend Feature
1. Create component in `frontend/src/components/`
2. Add to appropriate page
3. Update state management if needed
4. Add TypeScript types
5. Update README if user-facing

## Debugging

### Backend
```bash
# Enable debug mode
DEBUG=True uvicorn app.main:app --reload --log-level debug

# Check logs
tail -f backend/logs/app.log
```

### Frontend
```bash
# Development mode with hot reload
npm run dev

# Check console for errors
# Use React DevTools
```

## Docker Development

```bash
# Build and run with Docker
docker-compose up --build

# Run tests in Docker
docker-compose run backend pytest
docker-compose run frontend npm test

# Clean up
docker-compose down -v
```

## Common Issues

### Issue: Tests failing locally
**Solution**: Ensure all dependencies are installed
```bash
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### Issue: Import errors
**Solution**: Run from project root or set PYTHONPATH
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

### Issue: Docker build fails
**Solution**: Clear Docker cache
```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## Questions?

- Open an issue for bugs
- Start a discussion for questions
- Check existing issues first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Argus Intelligence Platform! 🔍✨
