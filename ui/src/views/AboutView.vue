<template>
  <div class="max-w-2xl space-y-6 pb-10">
    <!-- Hero -->
    <div class="card p-6 flex items-center gap-4">
      <div class="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center flex-shrink-0">
        <Dumbbell class="w-7 h-7 text-primary" />
      </div>
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">LiftJournal</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
          Дневник тренировок
          · <span class="font-semibold text-primary">v{{ APP_VERSION }}</span>
          · <span class="text-gray-400">{{ BUILD_DATE }}</span>
        </p>
        <p class="text-sm text-gray-600 dark:text-gray-300 mt-1">
          Ведите учёт тренировок, планируйте нагрузку и отслеживайте прогресс по каждому упражнению.
        </p>
      </div>
    </div>

    <!-- TOC -->
    <div class="card p-4">
      <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Содержание</p>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-1">
        <a v-for="section in sections" :key="section.id"
          :href="'#' + section.id"
          class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-primary transition-colors"
        >
          <component :is="section.icon" class="w-4 h-4 flex-shrink-0" />
          {{ section.title }}
        </a>
      </div>
    </div>

    <!-- Section: Запись тренировки -->
    <section :id="sections[0].id" class="space-y-3">
      <SectionHeader :icon="sections[0].icon" :title="sections[0].title" />

      <div class="card p-4 space-y-4">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Новая тренировка записывается за три шага. Нажмите кнопку <strong class="text-gray-800 dark:text-gray-200">+ Новая тренировка</strong> в боковом меню или на нижней панели.
        </p>

        <div class="space-y-3">
          <StepCard number="1" title="Основная информация">
            Введите название, выберите тип (Силовая, Кардио, HIIT и др.) и дату.
            Поле «Заметки» можно использовать для плана на тренировку или самочувствия.
            Нажмите <em>Начать тренировку</em> — запустится таймер.
          </StepCard>
          <StepCard number="2" title="Упражнения">
            Добавляйте упражнения кнопкой <strong>+ Добавить</strong>.
            Веса и повторения из <strong>последней тренировки</strong> с этим упражнением подставляются автоматически.
            Перетащите упражнение за иконку ⠿ чтобы изменить порядок.
            Для каждого подхода:
            <ul class="mt-2 space-y-1 ml-4 list-disc text-gray-600 dark:text-gray-400">
              <li>Введите вес и количество повторений.</li>
              <li>Нажмите <span class="inline-flex w-5 h-5 rounded-full bg-green-500 items-center justify-center"><CheckIcon /></span> — подход выполнен, запустится таймер отдыха.</li>
              <li>Нажмите ещё раз — подход помечается <span class="text-red-500 font-medium">провальным</span> (не идёт в статистику и расчёт 1ПМ).</li>
              <li>Третье нажатие — сброс статуса.</li>
            </ul>
          </StepCard>
          <StepCard number="3" title="Завершение">
            Просмотрите сводку: время, упражнения, количество подходов.
            Добавьте заметки после тренировки и нажмите <em>Завершить тренировку</em>.
          </StepCard>
        </div>

        <InfoBox icon="💡">
          Если тренировка была начата, но вы случайно закрыли приложение — прогресс сохраняется в браузере и восстановится при следующем открытии страницы тренировки.
        </InfoBox>
        <InfoBox icon="⚠️" color="amber">
          Нажмите × в заголовке страницы, чтобы отменить текущую тренировку.
          Весь прогресс будет потерян — приложение попросит подтверждения.
        </InfoBox>
      </div>
    </section>

    <!-- Section: Таймер отдыха -->
    <section :id="sections[1].id" class="space-y-3">
      <SectionHeader :icon="sections[1].icon" :title="sections[1].title" />
      <div class="card p-4 space-y-3">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Таймер отдыха появляется автоматически после каждого выполненного подхода. По умолчанию — 90 секунд.
        </p>
        <ul class="text-sm space-y-2 text-gray-600 dark:text-gray-400 ml-4 list-disc">
          <li>Выберите пресет: <strong>1 мин / 1.5 мин / 2 мин / 3 мин</strong>.</li>
          <li>Кнопки <strong>−15 / +15</strong> корректируют время на ходу.</li>
          <li>Нажмите <em>Пропустить</em>, чтобы скрыть таймер.</li>
          <li>По окончании таймера телефон завибрирует (если разрешено).</li>
        </ul>
      </div>
    </section>

    <!-- Section: История -->
    <section :id="sections[2].id" class="space-y-3">
      <SectionHeader :icon="sections[2].icon" :title="sections[2].title" />
      <div class="card p-4 space-y-4">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Раздел <strong>История</strong> показывает все прошедшие тренировки и запланированные события. Два режима отображения переключаются иконками в правом верхнем углу.
        </p>

        <SubSection title="Режим «Календарь»">
          Каждый день с тренировкой отмечен цветными точками:
          <ul class="mt-2 space-y-1 ml-4 list-disc text-gray-600 dark:text-gray-400">
            <li><span class="inline-block w-2.5 h-2.5 rounded-full bg-indigo-500 mr-1"></span>Силовая тренировка</li>
            <li><span class="inline-block w-2.5 h-2.5 rounded-full bg-green-500 mr-1"></span>Кардио</li>
            <li><span class="inline-block w-2.5 h-2.5 rounded-full bg-amber-400 mr-1"></span>Запланированная тренировка</li>
          </ul>
          <p class="mt-2">Нажмите на день, чтобы увидеть список тренировок. В панели дня:</p>
          <ul class="mt-1 space-y-1 ml-4 list-disc text-gray-600 dark:text-gray-400">
            <li><strong>Сегодня и будущие даты</strong> — кнопка <em>Запланировать</em>.</li>
            <li><strong>Прошедшие даты</strong> — кнопка <em>Добавить тренировку</em> (ретроспективная запись).</li>
            <li>У запланированных тренировок — кнопки <em>Начать</em> и ✏️ редактировать.</li>
          </ul>
        </SubSection>

        <SubSection title="Режим «Список»">
          Отображаются все тренировки и планы текущего месяца, отсортированные по дате (новые — выше).
        </SubSection>

        <SubSection title="Навигация по месяцам">
          Используйте стрелки ‹ › рядом с названием месяца для перехода назад и вперёд.
        </SubSection>

        <SubSection title="Фильтры">
          Под статистикой находится панель фильтров:
          <ul class="mt-1 space-y-1 ml-4 list-disc text-gray-600 dark:text-gray-400">
            <li>Тип тренировки (Все / Силовая / Кардио / …)</li>
            <li>Поиск по названию или упражнению</li>
            <li>Диапазон дат</li>
          </ul>
        </SubSection>

        <InfoBox icon="💡">
          Нажмите на карточку тренировки, чтобы открыть детальную страницу. Там же можно отредактировать или удалить запись, а кнопка <em>Повторить</em> создаёт копию тренировки с теми же упражнениями — чтобы откорректировать и начать заново.
        </InfoBox>
      </div>
    </section>

    <!-- Section: Планирование -->
    <section :id="sections[3].id" class="space-y-3">
      <SectionHeader :icon="sections[3].icon" :title="sections[3].title" />
      <div class="card p-4 space-y-4">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Раздел <strong>Планирование</strong> позволяет заранее составить тренировочный день с упражнениями и подходами.
        </p>

        <SubSection title="Создание плана">
          Нажмите <em>+ Новый план</em>. Укажите название, тип, дату, добавьте упражнения.
          Чтобы запланировать регулярные тренировки — включите переключатель <strong>Каждую неделю</strong> и выберите количество недель (4–24).
          Все повторяющиеся события связаны между собой.
        </SubSection>

        <SubSection title="Управление планами">
          На карточке плана доступны действия:
          <ul class="mt-1 space-y-1 ml-4 list-disc text-gray-600 dark:text-gray-400">
            <li><strong>Начать</strong> — открывает форму записи тренировки с заранее заполненными упражнениями.</li>
            <li><strong>Пропустить</strong> — помечает тренировку как пропущенную.</li>
            <li><strong>Удалить</strong> — удалить только эту или эту и все следующие (для повторяющихся).</li>
          </ul>
        </SubSection>

        <InfoBox icon="💡">
          Запланированные тренировки видны прямо в Истории — в режиме календаря (янтарная точка) и в списке. Начать выполнение можно прямо оттуда.
        </InfoBox>
      </div>
    </section>

    <!-- Section: Упражнения -->
    <section :id="sections[4].id" class="space-y-3">
      <SectionHeader :icon="sections[4].icon" :title="sections[4].title" />
      <div class="card p-4 space-y-4">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Библиотека упражнений — каталог с фильтрацией по мышечным группам и поиском по названию.
        </p>
        <SubSection title="Страница упражнения">
          Откройте любое упражнение, чтобы увидеть:
          <ul class="mt-1 space-y-1 ml-4 list-disc text-gray-600 dark:text-gray-400">
            <li>Личные рекорды: максимальный вес, расчётный 1ПМ, лучший тоннаж за тренировку.</li>
            <li>График прогресса (вес / объём / расчётный 1ПМ) по всем тренировкам.</li>
            <li>Историю: каждая тренировка с этим упражнением — дата, лучший подход, тоннаж.</li>
          </ul>
        </SubSection>
        <InfoBox icon="💡">
          Расчётный 1ПМ вычисляется по формуле Эпли: <code class="bg-gray-100 dark:bg-gray-800 px-1 rounded">вес × (1 + повторения / 30)</code>.
          Провальные подходы в расчёт не включаются.
        </InfoBox>
      </div>
    </section>

    <!-- Section: Циклы -->
    <section :id="sections[5].id" class="space-y-3">
      <SectionHeader :icon="sections[5].icon" :title="sections[5].title" />
      <div class="card p-4 space-y-4">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Циклы — программы с процентами от 1ПМ. Подходят для периодизации (5/3/1, волновые нагрузки и др.).
        </p>
        <SubSection title="Как работает">
          <ul class="space-y-1 ml-4 list-disc text-gray-600 dark:text-gray-400">
            <li>Создайте цикл: добавьте тренировки, упражнения и подходы с процентом от 1ПМ и количеством повторений.</li>
            <li>Укажите 1ПМ для каждого упражнения в Профиле (раздел «Максимумы»).</li>
            <li>Запустите цикл кнопкой <em>Начать цикл</em> — приложение рассчитает веса автоматически.</li>
            <li>Выполняйте тренировки по порядку; выполненные помечаются галочкой.</li>
          </ul>
        </SubSection>
        <InfoBox icon="💡">
          Если 1ПМ не задан, вес в подходах будет равен 0 — его можно ввести вручную во время тренировки.
        </InfoBox>
      </div>
    </section>

    <!-- Section: Профиль -->
    <section :id="sections[6].id" class="space-y-3">
      <SectionHeader :icon="sections[6].icon" :title="sections[6].title" />
      <div class="card p-4 space-y-4">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Раздел профиля доступен через аватар в правом верхнем углу (на мобильных) или через боковое меню.
        </p>
        <SubSection title="Тепловая карта активности">
          График в стиле GitHub — 52 недели, каждая ячейка = один день.
          Интенсивность цвета отражает количество тренировок в этот день.
        </SubSection>
        <SubSection title="Дневник веса">
          Добавляйте замеры веса тела. График показывает динамику.
        </SubSection>
        <SubSection title="Максимумы (1ПМ)">
          Вручную задайте свои рекорды по базовым движениям — они используются для расчёта нагрузки в Циклах.
        </SubSection>
        <SubSection title="Цели">
          Установите недельную цель по количеству тренировок.
          На главной странице истории отображается прогресс текущей недели.
        </SubSection>
      </div>
    </section>

    <!-- Section: Горячие клавиши / советы -->
    <section :id="sections[7].id" class="space-y-3">
      <SectionHeader :icon="sections[7].icon" :title="sections[7].title" />
      <div class="card divide-y divide-gray-100 dark:divide-gray-800">
        <TipRow v-for="tip in tips" :key="tip.label" :label="tip.label" :desc="tip.desc" />
      </div>
    </section>

    <!-- Section: Достижения -->
    <section :id="sections[8].id" class="space-y-3">
      <SectionHeader :icon="sections[8].icon" :title="sections[8].title" />
      <div class="card p-4 space-y-4">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Достижения открываются автоматически по результатам тренировок. Следить за прогрессом можно в разделе <strong>Профиль</strong>.
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <div v-for="a in ACHIEVEMENTS" :key="a.id" class="flex items-start gap-3 p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700">
            <span class="text-2xl flex-shrink-0 leading-none mt-0.5">{{ a.icon }}</span>
            <div class="min-w-0">
              <p class="text-sm font-semibold text-gray-800 dark:text-gray-200 leading-tight">{{ a.title }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ a.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section: История версий -->
    <section id="changelog" class="space-y-3">
      <SectionHeader :icon="historyIcon" title="История версий" />
      <div class="space-y-3">
        <div v-for="rel in CHANGELOG" :key="rel.version" class="card p-4">
          <div class="flex items-center gap-3 mb-3">
            <span class="font-bold text-primary text-sm">v{{ rel.version }}</span>
            <span v-if="rel.label" class="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">{{ rel.label }}</span>
            <span class="text-xs text-gray-400 ml-auto">{{ rel.date }}</span>
          </div>
          <ul class="space-y-1.5">
            <li v-for="entry in rel.entries" :key="entry.text" class="flex items-start gap-2 text-sm">
              <span :class="['mt-0.5 w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0 text-white text-[10px] font-bold',
                entry.type === 'feature' ? 'bg-primary' : entry.type === 'fix' ? 'bg-red-400' : 'bg-green-400']">
                {{ entry.type === 'feature' ? '★' : entry.type === 'fix' ? '✕' : '↑' }}
              </span>
              <span class="text-gray-600 dark:text-gray-400">{{ entry.text }}</span>
            </li>
          </ul>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { markRaw, h } from 'vue'
import {
  Dumbbell, ClipboardList, CalendarDays, BarChart3, User,
  Timer, Lightbulb, History, Check, Medal
} from 'lucide-vue-next'
import { APP_VERSION, BUILD_DATE } from '@/version.js'
import { CHANGELOG } from '@/changelog.js'

const historyIcon = markRaw(History)

// ── mini render-function components ─────────────────────────────────────────

const SectionHeader = (props) =>
  h('div', { class: 'flex items-center gap-2.5' }, [
    h('div', { class: 'w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0' },
      h(props.icon, { class: 'w-4 h-4 text-primary' })
    ),
    h('h2', { class: 'text-base font-bold text-gray-900 dark:text-white' }, props.title),
  ])
SectionHeader.props = ['icon', 'title']

const SubSection = {
  props: ['title'],
  setup(props, { slots }) {
    return () => h('div', { class: 'space-y-1' }, [
      h('p', { class: 'text-sm font-semibold text-gray-800 dark:text-gray-200' }, props.title),
      h('div', { class: 'text-sm text-gray-600 dark:text-gray-400' }, slots.default?.()),
    ])
  }
}

const StepCard = {
  props: ['number', 'title'],
  setup(props, { slots }) {
    return () => h('div', { class: 'flex gap-3' }, [
      h('div', { class: 'w-6 h-6 rounded-full bg-primary text-white text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5' }, props.number),
      h('div', { class: 'flex-1 text-sm text-gray-600 dark:text-gray-400' }, [
        h('p', { class: 'font-semibold text-gray-800 dark:text-gray-200 mb-0.5' }, props.title),
        slots.default?.(),
      ])
    ])
  }
}

const InfoBox = {
  props: { icon: String, color: { type: String, default: 'indigo' } },
  setup(props, { slots }) {
    const bg = props.color === 'amber'
      ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800'
      : 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-800'
    return () => h('div', { class: `flex gap-2 p-3 rounded-xl border text-sm ${bg}` }, [
      h('span', { class: 'text-base leading-none flex-shrink-0 mt-0.5' }, props.icon),
      h('span', { class: 'text-gray-700 dark:text-gray-300' }, slots.default?.()),
    ])
  }
}

const CheckIcon = () => h(Check, { class: 'w-3 h-3 text-white' })

const TipRow = {
  props: ['label', 'desc'],
  setup(props) {
    return () => h('div', { class: 'flex items-start gap-3 px-4 py-3' }, [
      h('span', { class: 'text-sm font-medium text-gray-800 dark:text-gray-200 w-44 flex-shrink-0' }, props.label),
      h('span', { class: 'text-sm text-gray-500 dark:text-gray-400' }, props.desc),
    ])
  }
}

// ── Data ─────────────────────────────────────────────────────────────────────

const sections = [
  { id: 'workout',  title: 'Запись тренировки',   icon: markRaw(Dumbbell)      },
  { id: 'timer',    title: 'Таймер отдыха',        icon: markRaw(Timer)         },
  { id: 'history',  title: 'История тренировок',   icon: markRaw(ClipboardList) },
  { id: 'planning', title: 'Планирование',         icon: markRaw(CalendarDays)  },
  { id: 'exercises',title: 'Упражнения',           icon: markRaw(Dumbbell)      },
  { id: 'cycles',   title: 'Циклы',                icon: markRaw(BarChart3)     },
  { id: 'profile',  title: 'Профиль',              icon: markRaw(User)          },
  { id: 'tips',       title: 'Советы и подсказки',   icon: markRaw(Lightbulb) },
  { id: 'achievements', title: 'Достижения',          icon: markRaw(Medal)     },
  { id: 'changelog',   title: 'История версий',       icon: markRaw(History)   },
]

const ACHIEVEMENTS = [
  { id: 'first_workout',    icon: '🎯', title: 'Первый шаг',          description: 'Запишите первую тренировку' },
  { id: 'workouts_10',      icon: '🥉', title: 'Начало пути',          description: 'Завершите 10 тренировок' },
  { id: 'workouts_50',      icon: '🥈', title: 'Полтинник',            description: 'Завершите 50 тренировок' },
  { id: 'workouts_100',     icon: '🥇', title: 'Сотня',                description: 'Завершите 100 тренировок' },
  { id: 'streak_3',         icon: '🔥', title: 'Первая серия',         description: '3 тренировки подряд' },
  { id: 'streak_7',         icon: '💪', title: 'Неделя без пропусков', description: '7 тренировок подряд' },
  { id: 'streak_10',        icon: '🔥', title: 'На огне',              description: '10 тренировок подряд' },
  { id: 'streak_30',        icon: '🏆', title: 'Железная воля',        description: '30 тренировок подряд' },
  { id: 'volume_1t_month',  icon: '💣', title: 'Первая тонна',         description: '1 000 кг тоннажа за один месяц' },
  { id: 'volume_10t_month', icon: '🏋️', title: 'Десять тонн',          description: '10 000 кг за один месяц' },
  { id: 'volume_100t_total',icon: '🌐', title: 'Сотня тонн',           description: '100 000 кг суммарно' },
]

const tips = [
  { label: 'Автозаполнение весов',      desc: 'При добавлении упражнения подставляются веса из последней тренировки с ним.' },
  { label: 'Провальный подход',         desc: 'Нажмите на зелёную кнопку ещё раз — подход станет красным и не будет учтён в статистике и 1ПМ.' },
  { label: 'Повтор тренировки',         desc: 'На странице любой тренировки нажмите кнопку ↺ — откроется форма с теми же упражнениями.' },
  { label: 'Ретроспективная запись',    desc: 'В Истории (календарь) нажмите на прошедший день → «Добавить тренировку», чтобы занести пропущенную запись.' },
  { label: 'Перетаскивание упражнений', desc: 'Зажмите иконку ⠿ слева от названия упражнения и перетащите в нужное место.' },
  { label: 'Тёмная тема',              desc: 'Следует системным настройкам устройства.' },
  { label: 'Офлайн-работа',            desc: 'Незавершённая тренировка сохраняется в браузере и не теряется при перезагрузке.' },
  { label: 'Фильтр по месяцу',         desc: 'В Истории стрелки ‹ › позволяют листать месяцы назад и вперёд.' },
]
</script>
