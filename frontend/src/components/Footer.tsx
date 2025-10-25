export default function Footer() {
  return (
    <footer className="bg-slate-50 border-t border-slate-200">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <p className="text-slate-600 text-sm">
            Made by{' '}
            <a 
              href="https://github.com/pranavreddygaddam" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-slate-900 hover:text-lime-500 transition-colors font-medium"
            >
              Pranav Reddy Gaddam
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
}
