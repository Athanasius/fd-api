#!/usr/bin/perl -w
# vim: textwidth=0 wrapmargin=0 shiftwidth=2 tabstop=2 softtabstop

use strict;

use Data::Dumper;

use LWP;
use HTTP::Cookies;
use HTML::TreeBuilder;
use JSON;

use ED::FDAPI::Config;

$ENV{'TZ'} = 'UTC';
my $config = ED::FDAPI::Config->new(file => "config.txt");
if (!defined($config)) {
  failure("Couldn't find server-side config");
}

if (!defined($config->getconf('user_name'))) {
	die("No user_name in config\n");
}
if (!defined($config->getconf('user_password'))) {
	die("No user_password in config\n");
}

my $ua = LWP::UserAgent->new(
	'agent' => 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12B411',
	'requests_redirectable' => []
);
$ua->cookie_jar(HTTP::Cookies->new(file => "lwpcookies.txt", autosave => 1, ignore_discard => 1));
$ua->timeout(10);

my ($req, $res, $tree);
$req = HTTP::Request->new('GET', $config->getconf('url_base'));
#ua_debug_enable($ua);
$res = $ua->request($req);
#print $res->headers_as_string("\n");
if (! $res->is_success) {
#	printf STDERR "Failed url_base\nCode: %s\nMessage: %s\nContents: %s\n", $res->code, $res->message, Dumper($res->content);
	if ($res->code == 302 and $res->header('Location') eq $config->getconf('url_login')) {
		print "Login required, so performing that...\n";
		do_login();
	}
} else {
	#printf STDERR "url_base Success!\nContents: %s\n", Dumper($res->content);
	print "No login required\n";
}
print "Querying profile...\n";
$req = HTTP::Request->new('GET', $config->getconf('url_base') . $config->getconf('url_query'));
$res = $ua->request($req);
if (! $res->is_success) {
	#printf STDERR "Failed url_query\nCode: %s\nMessage: %s\nContents: %s\n", $res->code, $res->message, Dumper($res->content);
	if ($res->code == 302 and $res->header('Location') eq $config->getconf('url_login')) {
		die("Tried to query profile but was redirected to login, something went wrong.");
	}
} else {
	print "Profile retrieved\n";
	#printf STDERR "url_query Success!\nContents: %s\n", Dumper($res->content);
}

my $json = decode_json($res->content);
#print Dumper($json);
print $res->content;
exit(0);

sub do_login {
	$req = HTTP::Request->new('POST', $config->getconf('url_base') . $config->getconf('url_login'));
	$req->content_type('application/x-www-form-urlencoded');
	$req->content("email=" . $config->getconf('user_name') . "&password=" . $config->getconf('user_password'));
	$res = $ua->request($req); #, \%form);
#print $res->headers_as_string("\n");
	if (! $res->is_success) {
#		printf STDERR "Failed url_login\nCode: %s\nMessage: %s\nContents: %s\n", $res->code, $res->message, Dumper($res->content);
		if ($res->code == 429) {
			printf STDERR "429: %s - aborting\n", $res->message;
			exit(1);
		}
		if ($res->code == 302 and $res->header('Location') eq '/') {
			# Login succeeded, no need for auth code
			return
		}
		printf STDERR "Login succeeded, need auth code: %s, %s\n", $res->code, $res->message;
		# Login succeeded, check email for auth code.
		LOGIN_ENTER_CODE:
		print "Login succeeded, check email for authentication code and enter it below\nCode: ";
		my $code = readline;
		chomp($code);
		$req = HTTP::Request->new('POST', $config->getconf('url_base') . $config->getconf('url_confirm'));
		$req->content_type('application/x-www-form-urlencoded');
		$req->content("code=" . $code);
		$res = $ua->request($req); #, \%form);
#print $res->headers_as_string("\n");
		if (! $res->is_success) {
			#printf STDERR "Failed url_confirm\nCode: %s\nMessage: %s\nContents: %s\n", $res->code, $res->message, Dumper($res->content);
			if ($res->code == 302 and $res->header('Location') eq '/') {
				print "Confirmation code accepted...\n";
			} else {
				printf STDERR "Unknown redirect after sending confirmation code.\n";
			}
		} else {
			#printf STDERR "url_confirm Success!\nContents: %s\n", Dumper($res->content);
			print "Code wasn't recognised, did you typo it?\n";
			goto LOGIN_ENTER_CODE;
		}
	} else {
		printf STDERR "Unexpected 'OK' after login (should redirect to site root)\nContents: %s\n", Dumper($res->content);
	}

}

###########################################################################
# LWP::UserAgent Debugging
###########################################################################
sub ua_debug_enable {
	my $ua = shift;
	$ua->add_handler('request_send' => \&debug_ua_send, (m_scheme => 'https'));
	$ua->add_handler('response_redirect' => \&debug_ua_redirect, (m_scheme => 'https'));
}

sub ua_debug_disable {
	my $ua = shift;
	$ua->remove_handler('request_send', (m_scheme => 'https'));
	$ua->remove_handler('response_redirect', (m_scheme => 'https'));
}

sub debug_ua_send {
	my($request, $ua, $h) = @_;
	printf STDERR "Request: %s\n",
		$request->as_string,
	;
	return;
}

sub debug_ua_redirect {
	my($response, $ua, $h) = @_;
	printf STDERR "Redirect: %s\n",
		$response->as_string,
	;
	return;
}
###########################################################################
