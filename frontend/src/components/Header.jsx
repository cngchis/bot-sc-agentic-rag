export default function Header({ onClear }) {
  return (
    <div className="flex items-center justify-between px-3 py-3 sm:px-6 sm:py-4 bg-white text-gray-800 shadow">
      
      <div className="flex items-center gap-2 sm:gap-3">
        <img 
          src="/src/assets/logo.svg" 
          alt="Logo" 
          className="w-10 h-10 sm:w-20 sm:h-20" 
        />

        <div>
          <h1 className="font-bold text-sm sm:text-lg">
            Techcombank Assistant
          </h1>
          <p className="hidden sm:block text-xs text-gray-600">
            Hỗ trợ 24/7
          </p>
        </div>
      </div>

      <button
        onClick={onClear}
        className="text-xs sm:text-base bg-red-600 text-white hover:bg-red-800 px-2 py-1 sm:px-3 sm:py-1 rounded"
      >
        Xóa lịch sử
      </button>
    </div>
  );
}