import { useState, useRef, useCallback } from 'react'
import {
  RadialBarChart, RadialBar, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell,
  PieChart, Pie, Legend,
} from 'recharts'

const DISHES = [
  {
    name: 'Cơm tấm sườn bì chả',
    image: 'https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=600&h=400&fit=crop&auto=format',
    calories: 520,
    protein: 28,
    carbs: 58,
    fat: 18,
    fiber: 3.2,
    vitamins: 72,
    score: 74,
    items: ['Cơm tấm (200g)', 'Sườn nướng (80g)', 'Bì heo (30g)', 'Chả trứng (40g)', 'Dưa leo (50g)', 'Cà chua (30g)'],
    goodFeedback: ['Cung cấp đủ protein từ thịt sườn và chả.', 'Có rau tươi kèm theo (dưa leo, cà chua).', 'Năng lượng phù hợp cho buổi học sáng.'],
    warnFeedback: ['Hàm lượng chất xơ còn thấp — nên thêm rau xanh.', 'Chất béo từ bì heo khá cao, nên ăn vừa phải.'],
  },
  {
    name: 'Bánh mì thịt nguội',
    image: 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600&h=400&fit=crop&auto=format',
    calories: 380,
    protein: 18,
    carbs: 45,
    fat: 14,
    fiber: 2.1,
    vitamins: 55,
    score: 62,
    items: ['Bánh mì (100g)', 'Thịt nguội (60g)', 'Pate (20g)', 'Dưa leo (40g)', 'Hành ngò (10g)', 'Tương ớt (10g)'],
    goodFeedback: ['Dễ ăn, tiện lợi cho buổi sáng.', 'Có rau thơm và dưa leo.'],
    warnFeedback: ['Thiếu chất xơ và vitamin đáng kể.', 'Pate và thịt nguội chứa nhiều natri — không nên ăn mỗi ngày.', 'Nên bổ sung thêm 1 ly sữa hoặc trái cây.'],
  },
  {
    name: 'Phở bò tái chín',
    image: 'https://images.unsplash.com/photo-1618160702438-9b02ab6515c9?w=600&h=400&fit=crop&auto=format',
    calories: 450,
    protein: 32,
    carbs: 52,
    fat: 10,
    fiber: 4.5,
    vitamins: 85,
    score: 88,
    items: ['Bánh phở (150g)', 'Thịt bò tái (60g)', 'Thịt bò chín (40g)', 'Giá đỗ (50g)', 'Hành lá (15g)', 'Rau thơm (20g)'],
    goodFeedback: ['Protein cao, chất béo thấp — rất cân bằng.', 'Giàu chất xơ từ rau giá và rau thơm.', 'Đạt chuẩn dinh dưỡng bữa sáng học sinh.'],
    warnFeedback: ['Nước dùng có thể chứa nhiều natri — không uống hết nước.'],
  },
]

const NAV = [
  { icon: '🏠', label: 'Trang chủ' },
  { icon: '📷', label: 'Nhận diện món ăn' },
  { icon: '📊', label: 'Lịch sử dinh dưỡng' },
  { icon: '🎯', label: 'Mục tiêu cá nhân' },
  { icon: '📚', label: 'Kiến thức dinh dưỡng' },
  { icon: '⚙️', label: 'Cài đặt' },
]

const WEEKLY = [
  { day: 'T2', calo: 480, target: 500 },
  { day: 'T3', calo: 510, target: 500 },
  { day: 'T4', calo: 390, target: 500 },
  { day: 'T5', calo: 520, target: 500 },
  { day: 'T6', calo: 450, target: 500 },
  { day: 'T7', calo: 370, target: 500 },
  { day: 'CN', calo: 490, target: 500 },
]

function ScoreRing({ score }: { score: number }) {
  const color = score >= 80 ? '#047857' : score >= 60 ? '#10b981' : '#f97316'
  const data = [{ value: score }, { value: 100 - score }]
  return (
    <div className="relative w-32 h-32">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} cx="50%" cy="50%" innerRadius={42} outerRadius={58} startAngle={90} endAngle={-270} dataKey="value" strokeWidth={0}>
            <Cell fill={color} />
            <Cell fill="#e5e7eb" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-800 leading-none" style={{ color, fontFamily: 'DM Sans, sans-serif' }}>{score}</span>
        <span className="text-xs font-600 text-gray-400">/ 100</span>
      </div>
    </div>
  )
}

const MACRO_COLORS = ['#10b981', '#6ee7b7', '#fde68a', '#f97316']

function getBmiCategory(bmi: number) {
  if (bmi < 18.5) return { label: 'Thiếu cân', color: '#f97316' }
  if (bmi < 23) return { label: 'Bình thường', color: '#10b981' }
  if (bmi < 27.5) return { label: 'Thừa cân', color: '#f97316' }
  return { label: 'Béo phì', color: '#ef4444' }
}

export default function App() {
  const [activeNav, setActiveNav] = useState(1)
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState<typeof DISHES[0] | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [sampleIdx, setSampleIdx] = useState(0)
  const fileRef = useRef<HTMLInputElement>(null)

  // Student info state
  const [grade, setGrade] = useState<'10' | '11' | '12' | ''>('')
  const [height, setHeight] = useState('')
  const [weight, setWeight] = useState('')

  const bmi = height && weight
    ? parseFloat((parseFloat(weight) / Math.pow(parseFloat(height) / 100, 2)).toFixed(1))
    : null
  const bmiCat = bmi ? getBmiCategory(bmi) : null

  const handleFile = useCallback((file: File) => {
    const url = URL.createObjectURL(file)
    setPreview(url)
    setResult(null)
    setUploading(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }, [handleFile])

  const handleAnalyze = () => {
    setAnalyzing(true)
    setTimeout(() => {
      setResult(DISHES[sampleIdx % DISHES.length])
      setSampleIdx(i => i + 1)
      setAnalyzing(false)
    }, 2200)
  }

  const macroData = result ? [
    { name: 'Protein', value: result.protein, unit: 'g' },
    { name: 'Tinh bột', value: result.carbs, unit: 'g' },
    { name: 'Chất béo', value: result.fat, unit: 'g' },
    { name: 'Chất xơ', value: result.fiber, unit: 'g' },
  ] : []

  return (
    <div className="flex min-h-screen" style={{ background: '#f9fafb' }}>
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 flex flex-col" style={{ background: '#ecfdf5', borderRight: '1.5px solid #e5e7eb', minHeight: '100vh' }}>
        {/* Logo */}
        <div className="px-6 pt-8 pb-6">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl" style={{ background: '#047857' }}>🥗</div>
            <div>
              <div className="text-sm font-800 leading-tight" style={{ color: '#047857', fontFamily: 'DM Sans, sans-serif' }}>NutriScan</div>
              <div className="text-xs font-500" style={{ color: '#6b7280' }}>Dinh dưỡng học đường</div>
            </div>
          </div>
        </div>

        {/* Student Info Form */}
        <div className="mx-4 mb-4 p-4 rounded-xl" style={{ background: '#fff', border: '1.5px solid #a7f3d0' }}>
          <div className="text-xs font-800 uppercase tracking-wide mb-3" style={{ color: '#047857' }}>👤 Thông tin học sinh</div>

          {/* Grade checkboxes */}
          <div className="mb-3">
            <label className="text-xs font-700 block mb-2" style={{ color: '#374151' }}>Khối lớp</label>
            <div className="flex gap-2">
              {(['10', '11', '12'] as const).map(g => (
                <label key={g} className="flex items-center gap-1.5 cursor-pointer">
                  <div
                    className="w-4 h-4 rounded flex items-center justify-center flex-shrink-0"
                    style={{
                      background: grade === g ? '#10b981' : '#fff',
                      border: `2px solid ${grade === g ? '#10b981' : '#a7f3d0'}`,
                      transition: 'all 0.15s',
                    }}
                    onClick={() => setGrade(grade === g ? '' : g)}
                  >
                    {grade === g && <span className="text-white" style={{ fontSize: 9, lineHeight: 1, fontWeight: 800 }}>✓</span>}
                  </div>
                  <span className="text-xs font-600" style={{ color: grade === g ? '#047857' : '#6b7280' }}>Lớp {g}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Height & Weight */}
          <div className="flex gap-2 mb-3">
            <div className="flex-1">
              <label className="text-xs font-700 block mb-1" style={{ color: '#374151' }}>Chiều cao (cm)</label>
              <input
                type="number"
                value={height}
                onChange={e => setHeight(e.target.value)}
                placeholder="160"
                min={100} max={220}
                className="w-full text-xs px-3 py-2 rounded-lg outline-none"
                style={{ border: '1.5px solid #a7f3d0', background: '#f9fafb', color: '#111827', fontFamily: 'Nunito, sans-serif' }}
              />
            </div>
            <div className="flex-1">
              <label className="text-xs font-700 block mb-1" style={{ color: '#374151' }}>Cân nặng (kg)</label>
              <input
                type="number"
                value={weight}
                onChange={e => setWeight(e.target.value)}
                placeholder="50"
                min={20} max={200}
                className="w-full text-xs px-3 py-2 rounded-lg outline-none"
                style={{ border: '1.5px solid #a7f3d0', background: '#f9fafb', color: '#111827', fontFamily: 'Nunito, sans-serif' }}
              />
            </div>
          </div>

          {/* BMI Result */}
          {bmi && bmiCat && (
            <div className="rounded-xl px-3 py-3 flex items-center justify-between" style={{ background: '#ecfdf5', border: '1.5px solid #a7f3d0' }}>
              <div>
                <div className="text-xs font-600" style={{ color: '#6b7280' }}>Chỉ số BMI</div>
                <div className="text-xl font-800 leading-tight" style={{ color: '#047857', fontFamily: 'DM Sans, sans-serif' }}>{bmi}</div>
              </div>
              <div className="text-right">
                <span className="text-xs font-700 px-2 py-1 rounded-full" style={{ background: bmiCat.color, color: '#fff' }}>
                  {bmiCat.label}
                </span>
                <div className="text-xs mt-1 font-500" style={{ color: '#6b7280' }}>
                  {bmi < 18.5 ? 'Nên ăn thêm' : bmi < 23 ? 'Duy trì tốt!' : 'Nên điều chỉnh'}
                </div>
              </div>
            </div>
          )}
          {!bmi && (
            <div className="text-xs text-center py-2 rounded-xl" style={{ color: '#9ca3af', background: '#f9fafb', border: '1px dashed #d1fae5' }}>
              Nhập chiều cao & cân nặng để tính BMI
            </div>
          )}
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 space-y-1">
          {NAV.map((item, i) => (
            <div key={i} className={`sidebar-link${activeNav === i ? ' active' : ''}`} onClick={() => setActiveNav(i)}>
              <span className="text-base">{item.icon}</span>
              <span className="text-sm">{item.label}</span>
              {i === 1 && (
                <span className="ml-auto text-xs px-1.5 py-0.5 rounded-full font-700" style={{ background: '#10b981', color: '#fff' }}>Mới</span>
              )}
            </div>
          ))}
        </nav>

        <div className="mx-4 mb-4" style={{ height: 1, background: '#e5e7eb' }} />
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col overflow-y-auto">
        {/* Header */}
        <header className="sticky top-0 z-10 px-8 py-4 flex items-center justify-between" style={{ background: '#fff', borderBottom: '1.5px solid #e5e7eb' }}>
          <div>
            <h1 className="text-xl font-800 leading-tight" style={{ color: '#047857', fontFamily: 'DM Sans, sans-serif' }}>
              Nhận diện & Đánh giá Dinh dưỡng Bữa Sáng
            </h1>
            <p className="text-sm font-500 mt-0.5" style={{ color: '#6b7280' }}>
              Chụp hoặc tải ảnh món ăn để nhận phân tích dinh dưỡng tức thì từ AI
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-sm font-600 px-3 py-1.5 rounded-full" style={{ background: '#ecfdf5', color: '#047857', border: '1px solid #a7f3d0' }}>
              🕐 Thứ Ba, 18/08/2026
            </div>
            <div className="w-9 h-9 rounded-full flex items-center justify-center text-white font-700 text-sm" style={{ background: '#10b981' }}>👤</div>
          </div>
        </header>

        <div className="flex-1 px-8 py-6 space-y-6">
          {/* Upload + Result Row */}
          <div className="grid gap-6" style={{ gridTemplateColumns: result ? '1fr 1fr' : '1fr' }}>
            {/* Upload Zone */}
            <div className="bg-white rounded-2xl p-6 shadow-sm" style={{ border: '1.5px solid #e5e7eb' }}>
              <h2 className="text-base font-800 mb-4" style={{ color: '#047857', fontFamily: 'DM Sans, sans-serif' }}>
                📷 Tải ảnh món ăn
              </h2>

              {!preview ? (
                <div
                  className="upload-zone flex flex-col items-center justify-center py-14 cursor-pointer"
                  style={{ minHeight: 220 }}
                  onDrop={handleDrop}
                  onDragOver={e => e.preventDefault()}
                  onClick={() => fileRef.current?.click()}
                >
                  <div className="text-5xl mb-3">🍱</div>
                  <p className="text-sm font-700 mb-1" style={{ color: '#047857' }}>Kéo thả ảnh vào đây</p>
                  <p className="text-xs font-500 mb-4" style={{ color: '#6b7280' }}>hoặc nhấn để chọn từ thiết bị</p>
                  <button className="btn-primary px-5 py-2 text-sm">Chọn ảnh</button>
                  <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])} />
                </div>
              ) : (
                <div>
                  <div className="relative rounded-xl overflow-hidden mb-4" style={{ height: 220 }}>
                    <img src={preview} alt="khay ăn" className="w-full h-full object-cover" />
                    <button
                      className="absolute top-2 right-2 text-xs px-2 py-1 rounded-lg font-600"
                      style={{ background: 'rgba(255,255,255,0.9)', color: '#047857' }}
                      onClick={() => { setPreview(null); setResult(null) }}
                    >✕ Xóa</button>
                  </div>
                  <button
                    className="btn-primary w-full py-3 text-sm flex items-center justify-center gap-2"
                    onClick={handleAnalyze}
                    disabled={analyzing}
                  >
                    {analyzing ? (
                      <>
                        <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full spin-slow" />
                        Đang phân tích AI...
                      </>
                    ) : '🔍 Phân tích dinh dưỡng'}
                  </button>
                </div>
              )}

              {/* Sample images */}
              <div className="mt-4">
                <p className="text-xs font-600 mb-2" style={{ color: '#6b7280' }}>Thử với ảnh mẫu:</p>
                <div className="flex gap-2">
                  {DISHES.map((d, i) => (
                    <button
                      key={i}
                      className="rounded-xl overflow-hidden flex-1 h-16 relative group"
                      style={{ border: '2px solid #a7f3d0' }}
                      onClick={() => { setPreview(d.image); setResult(null) }}
                    >
                      <img src={d.image} alt={d.name} className="w-full h-full object-cover" />
                      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 flex items-center justify-center text-xs font-700 text-white transition-opacity" style={{ background: 'rgba(4,120,87,0.7)' }}>Chọn</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Result Panel */}
            {result && (
              <div className="bg-white rounded-2xl p-6 shadow-sm" style={{ border: '1.5px solid #e5e7eb' }}>
                <div className="flex items-start gap-4 mb-5">
                  <div className="rounded-xl overflow-hidden flex-shrink-0" style={{ width: 80, height: 80 }}>
                    <img src={result.image} alt={result.name} className="w-full h-full object-cover" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-base font-800 mb-0.5" style={{ color: '#047857', fontFamily: 'DM Sans, sans-serif' }}>{result.name}</h3>
                    <p className="text-xs font-500 mb-2" style={{ color: '#6b7280' }}>Phân tích bởi NutriScan AI</p>
                    <div className="flex flex-wrap gap-1">
                      {result.items.map((item, i) => (
                        <span key={i} className="text-xs px-2 py-0.5 rounded-full font-500" style={{ background: '#ecfdf5', color: '#047857' }}>{item}</span>
                      ))}
                    </div>
                  </div>
                  <ScoreRing score={result.score} />
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-3 mb-5">
                  {[
                    { label: 'Tổng Calo', val: result.calories, unit: 'kcal', icon: '🔥' },
                    { label: 'Protein', val: result.protein, unit: 'g', icon: '💪' },
                    { label: 'Chất xơ', val: result.fiber, unit: 'g', icon: '🥦' },
                    { label: 'Tinh bột', val: result.carbs, unit: 'g', icon: '🌾' },
                  ].map((m, i) => (
                    <div key={i} className="metric-card px-4 py-3 flex items-center gap-3">
                      <span className="text-2xl">{m.icon}</span>
                      <div>
                        <div className="text-lg font-800 leading-none" style={{ color: '#047857', fontFamily: 'DM Sans, sans-serif' }}>{m.val}<span className="text-xs font-600 ml-1" style={{ color: '#6b7280' }}>{m.unit}</span></div>
                        <div className="text-xs font-600 mt-0.5" style={{ color: '#6b7280' }}>{m.label}</div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Feedback */}
                <div className="space-y-2">
                  {result.goodFeedback.map((f, i) => (
                    <div key={i} className="tip-good px-4 py-2 text-sm font-600" style={{ color: '#065f46' }}>✅ {f}</div>
                  ))}
                  {result.warnFeedback.map((f, i) => (
                    <div key={i} className="tip-warn px-4 py-2 text-sm font-600" style={{ color: '#c2410c' }}>⚠️ {f}</div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Charts Row */}
          {result && (
            <div className="grid grid-cols-2 gap-6">
              {/* Macro Breakdown */}
              <div className="bg-white rounded-2xl p-6 shadow-sm" style={{ border: '1.5px solid #e5e7eb' }}>
                <h3 className="text-sm font-800 mb-4" style={{ color: '#047857', fontFamily: 'DM Sans, sans-serif' }}>Phân bổ nhóm chất dinh dưỡng</h3>
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie data={macroData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, value }) => `${name}: ${value}g`} labelLine fontSize={11}>
                      {macroData.map((_, i) => <Cell key={i} fill={MACRO_COLORS[i]} />)}
                    </Pie>
                    <Tooltip formatter={(v, n) => [`${v}g`, n]} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Weekly calories */}
              <div className="bg-white rounded-2xl p-6 shadow-sm" style={{ border: '1.5px solid #e5e7eb' }}>
                <h3 className="text-sm font-800 mb-4" style={{ color: '#047857', fontFamily: 'DM Sans, sans-serif' }}>Calo bữa sáng trong tuần (kcal)</h3>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={WEEKLY} barSize={28}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                    <XAxis dataKey="day" tick={{ fontSize: 12, fill: '#6b7280', fontWeight: 600 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 11, fill: '#6b7280' }} axisLine={false} tickLine={false} domain={[0, 600]} />
                    <Tooltip
                      contentStyle={{ borderRadius: 10, border: '1px solid #a7f3d0', fontSize: 12 }}
                      formatter={(v) => [`${v} kcal`, 'Calo']}
                    />
                    <Bar dataKey="calo" radius={[6, 6, 0, 0]}>
                      {WEEKLY.map((d, i) => (
                        <Cell key={i} fill={d.calo >= d.target ? '#10b981' : '#f97316'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
                <div className="flex gap-4 mt-2">
                  <div className="flex items-center gap-1.5 text-xs font-600" style={{ color: '#6b7280' }}><span className="w-3 h-3 rounded-sm inline-block" style={{ background: '#10b981' }} />Đạt mục tiêu</div>
                  <div className="flex items-center gap-1.5 text-xs font-600" style={{ color: '#6b7280' }}><span className="w-3 h-3 rounded-sm inline-block" style={{ background: '#f97316' }} />Chưa đạt</div>
                </div>
              </div>
            </div>
          )}

          {/* Nutrition Summary Cards (always visible) */}
          <div className="bg-white rounded-2xl p-6 shadow-sm" style={{ border: '1.5px solid #e5e7eb' }}>
            <h3 className="text-sm font-800 mb-4" style={{ color: '#047857', fontFamily: 'DM Sans, sans-serif' }}>📋 Khuyến nghị dinh dưỡng bữa sáng — Học sinh THPT</h3>
            <div className="grid grid-cols-4 gap-4">
              {[
                { icon: '🔥', label: 'Năng lượng', val: '450–550', unit: 'kcal', note: '25–30% tổng ngày' },
                { icon: '💪', label: 'Protein', val: '18–30', unit: 'g', note: 'Thịt, trứng, đậu' },
                { icon: '🥦', label: 'Chất xơ', val: '≥ 5', unit: 'g', note: 'Rau, củ, quả' },
                { icon: '🌾', label: 'Tinh bột', val: '55–70', unit: 'g', note: 'Gạo, bánh mì nguyên cám' },
              ].map((r, i) => (
                <div key={i} className="metric-card px-4 py-4 text-center">
                  <div className="text-3xl mb-2">{r.icon}</div>
                  <div className="text-lg font-800" style={{ color: '#047857', fontFamily: 'DM Sans, sans-serif' }}>{r.val}<span className="text-xs font-600 ml-1" style={{ color: '#6b7280' }}>{r.unit}</span></div>
                  <div className="text-xs font-700 mt-0.5" style={{ color: '#374151' }}>{r.label}</div>
                  <div className="text-xs font-500 mt-0.5" style={{ color: '#9ca3af' }}>{r.note}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Tips */}
          <div className="bg-white rounded-2xl p-6 shadow-sm" style={{ border: '1.5px solid #e5e7eb' }}>
            <h3 className="text-sm font-800 mb-4" style={{ color: '#047857', fontFamily: 'DM Sans, sans-serif' }}>💡 Lời khuyên dinh dưỡng từ chuyên gia</h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { type: 'good', text: 'Bữa sáng nên ăn trong vòng 1 giờ sau khi thức dậy để kích hoạt trao đổi chất tốt nhất.' },
                { type: 'good', text: 'Kết hợp tinh bột phức hợp với protein giúp duy trì năng lượng ổn định qua các tiết học.' },
                { type: 'warn', text: 'Tránh bỏ bữa sáng — học sinh bỏ bữa sáng có khả năng tập trung thấp hơn 20%.' },
                { type: 'warn', text: 'Hạn chế đồ uống có đường vào buổi sáng — chọn sữa, nước trái cây tươi hoặc nước lọc.' },
              ].map((t, i) => (
                <div key={i} className={t.type === 'good' ? 'tip-good' : 'tip-warn'} style={{ padding: '12px 16px' }}>
                  <p className="text-sm font-600" style={{ color: t.type === 'good' ? '#065f46' : '#c2410c' }}>
                    {t.type === 'good' ? '✅' : '⚠️'} {t.text}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-2 px-8 py-5" style={{ background: '#047857', borderTop: '2px solid #065f46' }}>
          <div className="flex flex-col md:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full flex items-center justify-center text-lg" style={{ background: 'rgba(255,255,255,0.15)' }}>🏫</div>
              <div>
                <div className="text-sm font-800 text-white" style={{ fontFamily: 'DM Sans, sans-serif' }}>Trường THPT Nguyễn An Ninh</div>
                <div className="text-xs font-500" style={{ color: '#a7f3d0' }}>Địa chỉ: Số 93, Trần Nhân Tôn, Phường Vườn Lài. Tp. Hồ Chí Minh</div>
              </div>
            </div>
            <div className="flex items-center gap-6 text-xs font-600" style={{ color: '#a7f3d0' }}>
              <span>Điện thoại: (028) 38 330 591</span>
              <span>Email: nan@thptnan.edu.vn</span>
            </div>
            <div className="text-xs font-500" style={{ color: '#6ee7b7' }}>
            </div>
          </div>
        </footer>
      </main>
    </div>
  )
}
