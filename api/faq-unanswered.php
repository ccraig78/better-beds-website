<?php
// Better Beds FAQ Assistant unanswered-question endpoint.
// Hostinger/PHP deployment notes:
// 1. Set BB_FAQ_NOTIFY_EMAIL if you want a different destination.
// 2. Keep the private/ folder protected from public browsing.
// 3. This endpoint does not store payment data and should not be used for card/bank info.

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'method_not_allowed']);
    exit;
}

$raw = file_get_contents('php://input');
$data = json_decode($raw, true);
if (!is_array($data)) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'invalid_json']);
    exit;
}

function clean_text($value, $max = 1500) {
    $value = is_string($value) ? $value : '';
    $value = trim(preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $value));
    if (function_exists('mb_substr')) {
        return mb_substr($value, 0, $max);
    }
    return substr($value, 0, $max);
}

$question = clean_text($data['question'] ?? '', 1800);
$name = clean_text($data['name'] ?? '', 200);
$contact = clean_text($data['contact'] ?? '', 250);
$page = clean_text($data['page'] ?? '', 500);
$userAgent = clean_text($data['userAgent'] ?? ($_SERVER['HTTP_USER_AGENT'] ?? ''), 500);
$ip = $_SERVER['REMOTE_ADDR'] ?? '';

if ($question === '') {
    http_response_code(422);
    echo json_encode(['ok' => false, 'error' => 'question_required']);
    exit;
}

$entry = [
    'receivedAt' => gmdate('c'),
    'question' => $question,
    'name' => $name,
    'contact' => $contact,
    'page' => $page,
    'ip' => $ip,
    'userAgent' => $userAgent,
    'status' => 'needs_answer'
];

$privateDir = dirname(__DIR__) . '/private';
if (!is_dir($privateDir)) {
    @mkdir($privateDir, 0750, true);
}
$queueFile = $privateDir . '/faq-unanswered.jsonl';
@file_put_contents($queueFile, json_encode($entry, JSON_UNESCAPED_SLASHES) . PHP_EOL, FILE_APPEND | LOCK_EX);

$to = getenv('BB_FAQ_NOTIFY_EMAIL') ?: 'info@betterbeds.pro';
$subject = 'Better Beds FAQ needs an answer';
$body = "A website visitor asked a question the FAQ assistant could not answer.\n\n"
    . "Question:\n{$question}\n\n"
    . "Name: " . ($name ?: '(not provided)') . "\n"
    . "Contact: " . ($contact ?: '(not provided)') . "\n"
    . "Page: " . ($page ?: '(unknown)') . "\n"
    . "Received: " . $entry['receivedAt'] . " UTC\n\n"
    . "Suggested workflow:\n"
    . "1. Reply to the customer if contact info was provided.\n"
    . "2. Have Euro/Buddy add the approved answer to data/faq-knowledge.json so the assistant knows it next time.\n\n"
    . "Safety reminder: do not collect card, bank, or payment info by email/chat.";

$headers = [
    'From: Better Beds FAQ Assistant <no-reply@betterbeds.pro>',
    'Reply-To: info@betterbeds.pro',
    'Content-Type: text/plain; charset=UTF-8'
];

$mailSent = @mail($to, $subject, $body, implode("\r\n", $headers));

echo json_encode(['ok' => true, 'mailSent' => $mailSent]);
