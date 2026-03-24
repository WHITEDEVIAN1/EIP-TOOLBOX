import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'
import toast from 'react-hot-toast'
import {
  ImageIcon, Sliders, Wand2, Crop, RotateCcw, FlipHorizontal,
  FileDown, Eye, Zap, Type, Info, Eraser, ZoomIn, Upload, Download,
  RefreshCw, ChevronRight, Layers
} from 'lucide-react'

const API = '/api/image'

// ─── Sidebar navigation items ─────────────────────────────────────────────────
const TOOLS = [
  { id: 'convert',    label: 'Convert',    icon: FileDown,       group: 'Basic' },
  { id: 'resize',     label: 'Resize',     icon: Sliders,        group: 'Basic' },
  { id: 'crop',       label: 'Crop',       icon: Crop,           group: 'Basic' },
  { id: 'rotate',     label: 'Rotate',     icon: RotateCcw,      group: 'Basic' },
  { id: 'flip',       label: 'Flip',       icon: FlipHorizontal, group: 'Basic' },
  { id: 'adjust',     label: 'Adjust',     icon: Sliders,        group: 'Enhance' },
  { id: 'filter',     label: 'Filters',    icon: Layers,         group: 'Enhance' },
  { id: 'compress',   label: 'Compress',   icon: Zap,            group: 'Enhance' },
  { id: 'grayscale',  label: 'Grayscale',  icon: Eye,            group: 'Enhance' },
  { id: 'invert',     label: 'Invert',     icon: RefreshCw,      group: 'Enhance' },
  { id: 'watermark',  label: 'Watermark',  icon: Type,           group: 'AI & More' },
  { id: 'bg-remove',  label: 'BG Remove',  icon: Eraser,         group: 'AI & More' },
  { id: 'upscale',    label: 'Upscale',    icon: ZoomIn,         group: 'AI & More' },
  { id: 'ocr',        label: 'OCR',        icon: Type,           group: 'AI & More' },
  { id: 'metadata',   label: 'Metadata',   icon: Info,           group: 'AI & More' },
]

const GROUPS = ['Basic', 'Enhance', 'AI & More']

// ─── Image upload + preview hook ───────────────────────────────────────────────
function useImageUpload() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)

  const onDrop = useCallback((accepted) => {
    const f = accepted[0]
    if (!f) return
    setFile(f)
    setResult(null)
    const url = URL.createObjectURL(f)
    setPreview(url)
  }, [])

  return { file, preview, result, setResult, onDrop }
}

// ─── Generic form field ────────────────────────────────────────────────────────
function Field({ label, children }) {
  return (
    <div className="control-group">
      <label className="control-label">{label}</label>
      {children}
    </div>
  )
}

function Select({ value, onChange, options }) {
  return (
    <select className="control-input" value={value} onChange={e => onChange(e.target.value)}>
      {options.map(o => <option key={o.value ?? o} value={o.value ?? o}>{o.label ?? o}</option>)}
    </select>
  )
}

function Slider({ value, onChange, min = 0, max = 3, step = 0.1 }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <input
        type="range" className="control-input" style={{ flex: 1 }}
        min={min} max={max} step={step}
        value={value} onChange={e => onChange(parseFloat(e.target.value))}
      />
      <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', minWidth: '2.5rem' }}>{value}</span>
    </div>
  )
}

// ─── Dropzone component ────────────────────────────────────────────────────────
function DropZone({ onDrop }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'image/*': [] }, maxFiles: 1
  })
  return (
    <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`} id="dropzone">
      <input {...getInputProps()} />
      <div className="dropzone-icon"><Upload size={22} /></div>
      <div className="dropzone-title">{isDragActive ? 'Drop it!' : 'Drop image here'}</div>
      <div className="dropzone-sub">or click to browse · PNG JPG WEBP BMP GIF TIFF</div>
    </div>
  )
}

// ─── Preview area ──────────────────────────────────────────────────────────────
function PreviewArea({ original, result, onDownload }) {
  return (
    <div className="preview-area">
      <div className="preview-panel animate-in">
        <div className="preview-panel-header"><span>Original</span></div>
        {original
          ? <img src={original} className="preview-img" alt="Original" />
          : <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>No image uploaded</div>
        }
      </div>
      <div className="preview-panel animate-in" style={{ animationDelay: '0.05s' }}>
        <div className="preview-panel-header">
          <span>Result</span>
          {result && (
            <button className="btn btn-success btn-sm" onClick={onDownload} id="download-btn">
              <Download size={14} /> Download
            </button>
          )}
        </div>
        {result
          ? <img src={result} className="preview-img" alt="Result" />
          : <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>Result will appear here</div>
        }
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
// Tool panels
// ═══════════════════════════════════════════════════════════════════════════════

function ConvertPanel({ file, setResult }) {
  const [format, setFormat] = useState('webp')
  const [quality, setQuality] = useState(90)
  const [loading, setLoading] = useState(false)

  const run = async () => {
    if (!file) return toast.error('Upload an image first.')
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('format', format)
      fd.append('quality', quality)
      const res = await axios.post(`${API}/convert`, fd)
      setResult(res.data.url)
      toast.success(`Converted to ${format.toUpperCase()}!`)
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setLoading(false) }
  }

  return (
    <div className="card animate-in">
      <div className="card-title"><FileDown size={16} /> Convert Format</div>
      <div className="controls-grid">
        <Field label="Target Format">
          <Select value={format} onChange={setFormat} options={['png','jpg','webp','bmp','tiff','ico']} />
        </Field>
        <Field label={`Quality: ${quality}`}>
          <Slider value={quality} onChange={setQuality} min={1} max={100} step={1} />
        </Field>
      </div>
      <button className="btn btn-primary btn-full" style={{ marginTop: '1rem' }} onClick={run} disabled={loading} id="btn-convert">
        {loading ? <><div className="spinner" /> Converting…</> : <><ChevronRight size={16} /> Convert</>}
      </button>
    </div>
  )
}

function ResizePanel({ file, setResult }) {
  const [width, setWidth] = useState('')
  const [height, setHeight] = useState('')
  const [keepAspect, setKeepAspect] = useState(true)
  const [resample, setResample] = useState('lanczos')
  const [loading, setLoading] = useState(false)

  const run = async () => {
    if (!file) return toast.error('Upload an image first.')
    if (!width && !height) return toast.error('Enter Width or Height.')
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      if (width) fd.append('width', width)
      if (height) fd.append('height', height)
      fd.append('keep_aspect', keepAspect)
      fd.append('resample', resample)
      const res = await axios.post(`${API}/resize`, fd)
      setResult(res.data.url)
      toast.success('Resized!')
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setLoading(false) }
  }

  return (
    <div className="card animate-in">
      <div className="card-title"><Sliders size={16} /> Resize</div>
      <div className="controls-grid">
        <Field label="Width (px)">
          <input className="control-input" type="number" placeholder="e.g. 1920" value={width} onChange={e => setWidth(e.target.value)} />
        </Field>
        <Field label="Height (px)">
          <input className="control-input" type="number" placeholder="e.g. 1080" value={height} onChange={e => setHeight(e.target.value)} />
        </Field>
        <Field label="Resample">
          <Select value={resample} onChange={setResample} options={['lanczos','bicubic','bilinear','nearest']} />
        </Field>
        <Field label="Keep Aspect Ratio">
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
            <input type="checkbox" checked={keepAspect} onChange={e => setKeepAspect(e.target.checked)} />
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{keepAspect ? 'Yes' : 'No'}</span>
          </label>
        </Field>
      </div>
      <button className="btn btn-primary btn-full" style={{ marginTop: '1rem' }} onClick={run} disabled={loading} id="btn-resize">
        {loading ? <><div className="spinner" /> Resizing…</> : <><ChevronRight size={16} /> Resize</>}
      </button>
    </div>
  )
}

function CropPanel({ file, setResult }) {
  const [left, setLeft] = useState(0)
  const [top, setTop] = useState(0)
  const [right, setRight] = useState(400)
  const [bottom, setBottom] = useState(300)
  const [loading, setLoading] = useState(false)

  const run = async () => {
    if (!file) return toast.error('Upload an image first.')
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('left', left); fd.append('top', top)
      fd.append('right', right); fd.append('bottom', bottom)
      const res = await axios.post(`${API}/crop`, fd)
      setResult(res.data.url)
      toast.success('Cropped!')
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setLoading(false) }
  }

  return (
    <div className="card animate-in">
      <div className="card-title"><Crop size={16} /> Crop</div>
      <div className="controls-grid">
        {[['Left', left, setLeft], ['Top', top, setTop], ['Right', right, setRight], ['Bottom', bottom, setBottom]].map(([label, val, set]) => (
          <Field key={label} label={`${label} (px)`}>
            <input className="control-input" type="number" min={0} value={val} onChange={e => set(+e.target.value)} />
          </Field>
        ))}
      </div>
      <button className="btn btn-primary btn-full" style={{ marginTop: '1rem' }} onClick={run} disabled={loading} id="btn-crop">
        {loading ? <><div className="spinner" /> Cropping…</> : <><ChevronRight size={16} /> Crop</>}
      </button>
    </div>
  )
}

function RotatePanel({ file, setResult }) {
  const [angle, setAngle] = useState(90)
  const [loading, setLoading] = useState(false)

  const run = async () => {
    if (!file) return toast.error('Upload an image first.')
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file); fd.append('angle', angle)
      const res = await axios.post(`${API}/rotate`, fd)
      setResult(res.data.url)
      toast.success(`Rotated ${angle}°!`)
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setLoading(false) }
  }

  return (
    <div className="card animate-in">
      <div className="card-title"><RotateCcw size={16} /> Rotate</div>
      <div className="controls-grid">
        <Field label="Quick angles">
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {[90, 180, 270, 45, -90].map(a => (
              <button key={a} className={`btn btn-sm btn-secondary`} onClick={() => setAngle(a)}>{a}°</button>
            ))}
          </div>
        </Field>
        <Field label={`Angle: ${angle}°`}>
          <Slider value={angle} onChange={setAngle} min={-180} max={180} step={1} />
        </Field>
      </div>
      <button className="btn btn-primary btn-full" style={{ marginTop: '1rem' }} onClick={run} disabled={loading} id="btn-rotate">
        {loading ? <><div className="spinner" /> Rotating…</> : <><ChevronRight size={16} /> Rotate</>}
      </button>
    </div>
  )
}

function FlipPanel({ file, setResult }) {
  const [direction, setDirection] = useState('horizontal')
  const [loading, setLoading] = useState(false)

  const run = async () => {
    if (!file) return toast.error('Upload an image first.')
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file); fd.append('direction', direction)
      const res = await axios.post(`${API}/flip`, fd)
      setResult(res.data.url)
      toast.success('Flipped!')
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setLoading(false) }
  }

  return (
    <div className="card animate-in">
      <div className="card-title"><FlipHorizontal size={16} /> Flip</div>
      <Field label="Direction">
        <Select value={direction} onChange={setDirection} options={['horizontal','vertical','both']} />
      </Field>
      <button className="btn btn-primary btn-full" style={{ marginTop: '1rem' }} onClick={run} disabled={loading} id="btn-flip">
        {loading ? <><div className="spinner" /> Flipping…</> : <><ChevronRight size={16} /> Flip</>}
      </button>
    </div>
  )
}

function AdjustPanel({ file, setResult }) {
  const [brightness, setBrightness] = useState(1.0)
  const [contrast, setContrast] = useState(1.0)
  const [saturation, setSaturation] = useState(1.0)
  const [sharpness, setSharpness] = useState(1.0)
  const [loading, setLoading] = useState(false)

  const run = async () => {
    if (!file) return toast.error('Upload an image first.')
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('brightness', brightness); fd.append('contrast', contrast)
      fd.append('saturation', saturation); fd.append('sharpness', sharpness)
      const res = await axios.post(`${API}/adjust`, fd)
      setResult(res.data.url)
      toast.success('Adjustments applied!')
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setLoading(false) }
  }

  return (
    <div className="card animate-in">
      <div className="card-title"><Sliders size={16} /> Adjust</div>
      <div className="controls-grid" style={{ gridTemplateColumns: '1fr' }}>
        {[['Brightness', brightness, setBrightness], ['Contrast', contrast, setContrast],
          ['Saturation', saturation, setSaturation], ['Sharpness', sharpness, setSharpness]].map(([label, val, set]) => (
          <Field key={label} label={`${label}: ${val.toFixed(1)}`}>
            <Slider value={val} onChange={set} min={0} max={3} step={0.05} />
          </Field>
        ))}
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
        <button className="btn btn-secondary" onClick={() => { setBrightness(1); setContrast(1); setSaturation(1); setSharpness(1) }}>Reset</button>
        <button className="btn btn-primary" style={{ flex: 1 }} onClick={run} disabled={loading} id="btn-adjust">
          {loading ? <><div className="spinner" /> Applying…</> : <><ChevronRight size={16} /> Apply</>}
        </button>
      </div>
    </div>
  )
}

function FilterPanel({ file, setResult }) {
  const [filters, setFilters] = useState([])
  const [selected, setSelected] = useState(null)
  const [intensity, setIntensity] = useState(1.0)
  const [loading, setLoading] = useState(false)

  useState(() => {
    axios.get(`${API}/filters`)
      .then(r => setFilters(r.data.filters))
      .catch(() => {})
  }, [])

  const run = async () => {
    if (!file) return toast.error('Upload an image first.')
    if (!selected) return toast.error('Select a filter.')
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file); fd.append('filter_name', selected); fd.append('intensity', intensity)
      const res = await axios.post(`${API}/filter`, fd)
      setResult(res.data.url)
      toast.success(`Filter "${selected}" applied!`)
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setLoading(false) }
  }

  return (
    <div className="card animate-in">
      <div className="card-title"><Layers size={16} /> Filters</div>
      <div className="filter-grid">
        {filters.map(f => (
          <button key={f.name} title={f.description}
            className={`filter-chip ${selected === f.name ? 'selected' : ''}`}
            onClick={() => setSelected(f.name)}>
            {f.name.replace(/_/g, ' ')}
          </button>
        ))}
      </div>
      {selected && (
        <Field label={`Intensity: ${intensity.toFixed(1)}`} >
          <Slider value={intensity} onChange={setIntensity} min={0.1} max={3} step={0.1} />
        </Field>
      )}
      <button className="btn btn-primary btn-full" style={{ marginTop: '1rem' }}
        onClick={run} disabled={loading || !selected} id="btn-filter">
        {loading ? <><div className="spinner" /> Applying…</> : <><Wand2 size={16} /> Apply Filter</>}
      </button>
    </div>
  )
}

function CompressPanel({ file, setResult }) {
  const [quality, setQuality] = useState(75)
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState(null)

  const run = async () => {
    if (!file) return toast.error('Upload an image first.')
    setLoading(true); setStats(null)
    try {
      const fd = new FormData()
      fd.append('file', file); fd.append('quality', quality)
      const res = await axios.post(`${API}/compress`, fd)
      setResult(res.data.url); setStats(res.data)
      toast.success(`Saved ${res.data.saving_percent}%!`)
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setLoading(false) }
  }

  return (
    <div className="card animate-in">
      <div className="card-title"><Zap size={16} /> Compress</div>
      <Field label={`Quality: ${quality}`}>
        <Slider value={quality} onChange={setQuality} min={1} max={95} step={1} />
      </Field>
      {stats && (
        <div className="stats-bar" style={{ margin: '0.75rem 0' }}>
          <div className="stat-chip">Original <strong>{(stats.original_bytes/1024).toFixed(1)} KB</strong></div>
          <div className="stat-chip">Compressed <strong>{(stats.compressed_bytes/1024).toFixed(1)} KB</strong></div>
          <div className="stat-chip">Saved <strong style={{ color: '#10b981' }}>{stats.saving_percent}%</strong></div>
        </div>
      )}
      <button className="btn btn-primary btn-full" style={{ marginTop: '1rem' }} onClick={run} disabled={loading} id="btn-compress">
        {loading ? <><div className="spinner" /> Compressing…</> : <><Zap size={16} /> Compress</>}
      </button>
    </div>
  )
}

function SimpleActionPanel({ file, setResult, endpoint, icon: Icon, title, id }) {
  const [loading, setLoading] = useState(false)
  const run = async () => {
    if (!file) return toast.error('Upload an image first.')
    setLoading(true)
    try {
      const fd = new FormData(); fd.append('file', file)
      const res = await axios.post(`${API}/${endpoint}`, fd)
      setResult(res.data.url)
      toast.success(`${title} done!`)
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setLoading(false) }
  }
  return (
    <div className="card animate-in">
      <div className="card-title"><Icon size={16} /> {title}</div>
      <button className="btn btn-primary btn-full" onClick={run} disabled={loading} id={id}>
        {loading ? <><div className="spinner" /> Processing…</> : <><ChevronRight size={16} /> Apply {title}</>}
      </button>
    </div>
  )
}

function WatermarkPanel({ file, setResult }) {
  const [text, setText] = useState('ToolForge')
  const [position, setPosition] = useState('bottom-right')
  const [opacity, setOpacity] = useState(0.5)
  const [fontSize, setFontSize] = useState(36)
  const [color, setColor] = useState('white')
  const [loading, setLoading] = useState(false)

  const run = async () => {
    if (!file) return toast.error('Upload an image first.')
    if (!text.trim()) return toast.error('Enter watermark text.')
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file); fd.append('text', text)
      fd.append('position', position); fd.append('opacity', opacity)
      fd.append('font_size', fontSize); fd.append('color', color)
      const res = await axios.post(`${API}/watermark/text`, fd)
      setResult(res.data.url)
      toast.success('Watermark added!')
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setLoading(false) }
  }

  return (
    <div className="card animate-in">
      <div className="card-title"><Type size={16} /> Watermark</div>
      <div className="controls-grid">
        <Field label="Text">
          <input className="control-input" value={text} onChange={e => setText(e.target.value)} placeholder="Your watermark" />
        </Field>
        <Field label="Position">
          <Select value={position} onChange={setPosition}
            options={['top-left','top-right','bottom-left','bottom-right','center']} />
        </Field>
        <Field label={`Opacity: ${opacity.toFixed(1)}`}>
          <Slider value={opacity} onChange={setOpacity} min={0.1} max={1} step={0.05} />
        </Field>
        <Field label={`Font Size: ${fontSize}`}>
          <Slider value={fontSize} onChange={setFontSize} min={8} max={200} step={2} />
        </Field>
        <Field label="Color">
          <Select value={color} onChange={setColor} options={['white','black','red','yellow','blue','green','gray']} />
        </Field>
      </div>
      <button className="btn btn-primary btn-full" style={{ marginTop: '1rem' }} onClick={run} disabled={loading} id="btn-watermark">
        {loading ? <><div className="spinner" /> Adding…</> : <><ChevronRight size={16} /> Add Watermark</>}
      </button>
    </div>
  )
}

function OCRPanel({ file }) {
  const [lang, setLang] = useState('eng')
  const [loading, setLoading] = useState(false)
  const [text, setText] = useState('')

  const run = async () => {
    if (!file) return toast.error('Upload an image first.')
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file); fd.append('language', lang)
      const res = await axios.post(`${API}/ocr`, fd)
      setText(res.data.text)
      toast.success(`Found ${res.data.char_count} characters!`)
    } catch (e) { toast.error(e.response?.data?.detail || 'Tesseract not available') }
    finally { setLoading(false) }
  }

  return (
    <div className="card animate-in">
      <div className="card-title"><Type size={16} /> OCR — Extract Text</div>
      <Field label="Language">
        <Select value={lang} onChange={setLang} options={[
          { value:'eng', label:'English' }, { value:'hin', label:'Hindi' },
          { value:'fra', label:'French' }, { value:'deu', label:'German' },
          { value:'spa', label:'Spanish' }, { value:'chi_sim', label:'Chinese (Simplified)' },
        ]} />
      </Field>
      <button className="btn btn-primary btn-full" style={{ margin: '1rem 0 0.75rem' }} onClick={run} disabled={loading} id="btn-ocr">
        {loading ? <><div className="spinner" /> Reading…</> : <><Type size={16} /> Extract Text</>}
      </button>
      {text && <div className="ocr-result">{text || '(No text found)'}</div>}
    </div>
  )
}

function MetadataPanel({ file }) {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [stripping, setStripping] = useState(false)
  const [stripped, setStripped] = useState(null)

  const run = async () => {
    if (!file) return toast.error('Upload an image first.')
    setLoading(true)
    try {
      const fd = new FormData(); fd.append('file', file)
      const res = await axios.post(`${API}/metadata`, fd)
      setData(res.data)
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setLoading(false) }
  }

  const strip = async () => {
    if (!file) return
    setStripping(true)
    try {
      const fd = new FormData(); fd.append('file', file)
      const res = await axios.post(`${API}/metadata/strip`, fd)
      setStripped(res.data.url)
      toast.success('Metadata stripped!')
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setStripping(false) }
  }

  const mainFields = data ? Object.entries(data).filter(([k]) => k !== 'exif') : []

  return (
    <div className="card animate-in">
      <div className="card-title"><Info size={16} /> Metadata</div>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button className="btn btn-primary" style={{ flex: 1 }} onClick={run} disabled={loading} id="btn-metadata">
          {loading ? <><div className="spinner" /> Reading…</> : <><Info size={16} /> Read Metadata</>}
        </button>
        <button className="btn btn-secondary" onClick={strip} disabled={stripping} id="btn-strip">
          {stripping ? <div className="spinner" /> : <Eraser size={16} />} Strip
        </button>
        {stripped && <a className="btn btn-success" href={stripped} download>DL</a>}
      </div>
      {data && (
        <div style={{ marginTop: '1rem' }}>
          <table className="meta-table">
            <tbody>
              {mainFields.map(([k, v]) => (
                <tr key={k}><td>{k}</td><td>{String(v)}</td></tr>
              ))}
              {Object.entries(data.exif || {}).slice(0, 20).map(([k, v]) => (
                <tr key={k}><td>{k}</td><td>{String(v)}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function UpscalePanel({ file, setResult }) {
  const [scale, setScale] = useState(2)
  const [loading, setLoading] = useState(false)

  const run = async () => {
    if (!file) return toast.error('Upload an image first.')
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file); fd.append('scale', scale)
      const res = await axios.post(`${API}/upscale`, fd)
      setResult(res.data.url)
      toast.success(`Upscaled ${scale}x!`)
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setLoading(false) }
  }

  return (
    <div className="card animate-in">
      <div className="card-title"><ZoomIn size={16} /> Upscale</div>
      <Field label="Scale Factor">
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {[2, 4].map(s => (
            <button key={s} className={`btn ${scale === s ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setScale(s)}>{s}×</button>
          ))}
        </div>
      </Field>
      <button className="btn btn-primary btn-full" style={{ marginTop: '1rem' }} onClick={run} disabled={loading} id="btn-upscale">
        {loading ? <><div className="spinner" /> Upscaling…</> : <><ZoomIn size={16} /> Upscale {scale}×</>}
      </button>
    </div>
  )
}

// ─── Panel router ──────────────────────────────────────────────────────────────
function ToolPanel({ tool, file, setResult }) {
  const props = { file, setResult }
  switch (tool) {
    case 'convert':   return <ConvertPanel {...props} />
    case 'resize':    return <ResizePanel {...props} />
    case 'crop':      return <CropPanel {...props} />
    case 'rotate':    return <RotatePanel {...props} />
    case 'flip':      return <FlipPanel {...props} />
    case 'adjust':    return <AdjustPanel {...props} />
    case 'filter':    return <FilterPanel {...props} />
    case 'compress':  return <CompressPanel {...props} />
    case 'watermark': return <WatermarkPanel {...props} />
    case 'upscale':   return <UpscalePanel {...props} />
    case 'ocr':       return <OCRPanel file={file} />
    case 'metadata':  return <MetadataPanel file={file} />
    case 'grayscale': return <SimpleActionPanel {...props} endpoint="grayscale" icon={Eye} title="Grayscale" id="btn-grayscale" />
    case 'invert':    return <SimpleActionPanel {...props} endpoint="invert" icon={RefreshCw} title="Invert" id="btn-invert" />
    case 'bg-remove': return <SimpleActionPanel {...props} endpoint="bg-remove" icon={Eraser} title="BG Remove (AI)" id="btn-bgremove" />
    default: return null
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Main App
// ═══════════════════════════════════════════════════════════════════════════════
export default function App() {
  const [activeTool, setActiveTool] = useState('convert')
  const { file, preview, result, setResult, onDrop } = useImageUpload()

  const handleDownload = async () => {
    if (!result) return
    try {
      const resp = await fetch(result)
      const blob = await resp.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.style.display = 'none'
      a.href = url
      const ext = result.split('.').pop() || 'png'
      a.download = `toolforge_${activeTool}.${ext}`
      document.body.appendChild(a)
      a.click()
      setTimeout(() => {
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }, 500)
    } catch (e) {
      toast.error('Download failed')
    }
  }

  return (
    <div className="app">
      {/* ── Navbar ── */}
      <nav className="navbar">
        <div className="navbar-brand">
          <div className="navbar-logo">🔧</div>
          <span className="navbar-title">ToolForge</span>
          <span className="navbar-badge">Image Toolbox</span>
        </div>
        <div className="stats-bar">
          {file && <div className="stat-chip"><ImageIcon size={12} /><strong>{file.name}</strong></div>}
          <div className="stat-chip"><span>Open Source</span></div>
        </div>
      </nav>

      <div className="main-layout">
        {/* ── Sidebar ── */}
        <aside className="sidebar">
          {GROUPS.map(group => (
            <div key={group}>
              <div className="sidebar-label">{group}</div>
              <div className="sidebar-section">
                {TOOLS.filter(t => t.group === group).map(tool => {
                  const Icon = tool.icon
                  return (
                    <button key={tool.id} id={`nav-${tool.id}`}
                      className={`sidebar-item ${activeTool === tool.id ? 'active' : ''}`}
                      onClick={() => { setActiveTool(tool.id); setResult(null) }}>
                      <Icon className="icon" size={16} />
                      {tool.label}
                    </button>
                  )
                })}
              </div>
            </div>
          ))}
        </aside>

        {/* ── Content ── */}
        <main className="content">
          <div className="page-header">
            <h1 className="page-title">
              {TOOLS.find(t => t.id === activeTool)?.label ?? 'Image Toolbox'}
            </h1>
            <p className="page-sub">Open-source · Local processing · No uploads to cloud</p>
          </div>

          {/* Upload zone */}
          <DropZone onDrop={onDrop} />

          {/* Preview */}
          {(preview || result) && (
            <PreviewArea original={preview} result={result} onDownload={handleDownload} />
          )}

          {/* Tool panel */}
          <ToolPanel tool={activeTool} file={file} setResult={setResult} />
        </main>
      </div>
    </div>
  )
}
